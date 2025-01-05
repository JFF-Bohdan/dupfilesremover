import collections
import datetime
import os.path
import sys
import time
import datetime as dt

import humanize

from loguru import logger


from dupfilesremover import command_line_parser

from dupfilesremover import consts, misc, exceptions, file_system, data_types, weighting


import dataclasses
import pathlib
import typing

import itertools


def main():
    timestamp_begin = time.monotonic()
    perf_counters = data_types.PerfCounters()

    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")

    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args()

    folders = misc.normalize_folders(args.folders)
    try:
        misc.validate_folders(args.folders)
    except exceptions.FolderDoesNotExistsError as e:
        logger.error(e)
        sys.exit(1)

    files_masks = None
    if args.mask_sets:
        args.mask_sets = args.mask_sets.split(",")
        for mask in args.mask_sets:
            if not misc.is_mask_set_supported(mask):
                logger.error(
                    f"Mask set {mask} is not supported. Supported masks are: "
                    f"{list(consts.SUPPORTED_MASKS_SETS.keys())}"
                )
                sys.exit(1)

        files_masks = list(itertools.chain(*[consts.SUPPORTED_MASKS_SETS[mask] for mask in args.mask_sets]))

    weighted_folders = weighting.weight_folders(folders)
    logger.debug(f"Weighted folders: {weighted_folders}")

    debug_message = "\n\t".join(folders)
    logger.info(f"Folders to process:\n\t{debug_message}")

    files = misc.compute_hashes_for_files(
        misc.remove_files_with_unique_size(
            file_system.filter_files_by_masks(
                file_system.find_files_in_folders(
                    folders,
                    perf_counters,
                    recurse=args.recurse
                ),
                perf_counters,
                files_masks,
            ),
            perf_counters
        ),
        perf_counters
    )
    files = list(files)
    num_files = len(files)
    to_print = "\n\t".join([str(item) for item in files])
    logger.debug(f"Files ({num_files}):\n\t{to_print}")

    hash_to_files = misc.group_files_by_hash(files)
    logger.debug(f"Hash to files: {hash_to_files}")

    logger.info("Removing files with unique hashes...")
    hash_to_files = misc.filter_out_unique_files(
        hash_to_files,
        perf_counters
    )

    logger.info("Selecting files to keep...")
    hash_to_files = weighting.vote_and_sort_duplicates(hash_to_files, weighted_folders)
    logger.debug(f"hash_to_files = {hash_to_files}")

    for key, files in hash_to_files.items():
        if len(files) <= 1:
            raise RuntimeError("Error during attempt to delete files")

        logger.info(f"For hash {key}")

        file_to_save = files[0]  # .file_name
        files_to_delete = files[1:]  # [file.file_name for file in files[1:]]

        logger.info(f"File to keep: {file_to_save.file_name}")
        # logger.info(f"Files to remove: {files_to_delete}")

        file_system.remove_files(
            files=files_to_delete,
            perf_counters=perf_counters,
            dry_run=args.dry_run
        )

    human_readable_interval = humanize.precisedelta(
        dt.timedelta(seconds=time.monotonic() - timestamp_begin),
        minimum_unit="milliseconds"
    )

    dry_run_suffix = " [DRY RUN - no action performed]" if args.dry_run else ""
    logger.info(
        f"Stats:\n"
        f"\tTotal files count          : {perf_counters.total_files_count}\n"
        f"\tSkipped by mask            : {perf_counters.files_skipped_by_mask}\n"
        f"\tHashed data size           : {humanize.naturalsize(perf_counters.hashed_data_size)}\n"
        f"\tSkipped due to unique size : {perf_counters.files_skipped_due_to_unique_size}\n"
        f"\tSkipped due to unique hash : {perf_counters.files_skipped_due_to_unique_hash}\n"
        f"\tRemoved files count        : {perf_counters.removed_files_count}{dry_run_suffix}\n"
        f"\tReclaimed disk space       : {humanize.naturalsize(perf_counters.reclaimed_space)}{dry_run_suffix}\n"
    )
    logger.info(f"App finished @ {human_readable_interval}")
