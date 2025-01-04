import collections
import datetime
import os.path
import sys
import time
import datetime as dt

import humanize

from loguru import logger


from dupfilesremover import command_line_parser

from dupfilesremover import misc, exceptions, file_system, data_types, weighting


import dataclasses
import pathlib
import typing

import itertools





def group_files_by_hash(
        files: typing.Iterable[data_types.FileInfo]
) -> collections.defaultdict[str, list[data_types.FileInfo]]:
    result: collections.defaultdict[str, list[data_types.FileInfo]] = collections.defaultdict(list)
    for file in files:
        result[file.hash].append(file)

    return result


def filter_out_unique_files(
        hash_to_files: collections.defaultdict[str, list[data_types.FileInfo]],
        perf_counters: data_types.PerfCounters,
) -> dict[str, list[data_types.FileInfo]]:
    result: dict[str, list[data_types.FileInfo]] = {}

    keys = list(hash_to_files.keys())
    for key in keys:
        if len(hash_to_files[key]) == 1:
            logger.debug(f"Hash {key} contains only one file {hash_to_files[key][0]}, skipping")
            del hash_to_files[key]
            perf_counters.unique_files_count += 1
            continue

        result[key] = hash_to_files[key]

    return result


def main():
    timestamp_begin = time.monotonic()
    perf_counters = data_types.PerfCounters()

    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", level="INFO")

    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args()

    folders = misc.normalize_folders(args.folders)
    try:
        misc.validate_folders(args.folders)
    except exceptions.FolderDoesNotExistsError as e:
        logger.error(e)
        sys.exit(1)

    weighted_folders = weighting.weight_folders(folders)
    logger.debug(f"Weighted folders: {weighted_folders}")

    debug_message = "\n\t".join(folders)
    logger.info(f"Folders to process:\n\t{debug_message}")

    files = misc.compute_hashes_for_files(
        misc.remove_files_with_unique_size(
            file_system.find_target_files_in_folders(
                folders,
                perf_counters,
                recurse=args.recurse
            ),
            perf_counters
        ),
        perf_counters
    )
    files = list(files)
    num_files = len(files)
    to_print = "\n\t".join([str(item) for item in files])
    logger.debug(f"Files ({num_files}):\n\t{to_print}")

    hash_to_files = group_files_by_hash(files)
    logger.debug(f"Hash to files: {hash_to_files}")

    logger.info("Removing files with unique hashes...")
    hash_to_files = filter_out_unique_files(
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
        f"\tHashed data size           : {humanize.naturalsize(perf_counters.hashed_data_size)}\n"
        f"\tSkipped due to unique size : {perf_counters.files_skipped_due_to_unique_size}\n"
        f"\tSkipped due to unique hash : {perf_counters.unique_files_count}\n"
        f"\tRemoved files count        : {perf_counters.removed_files_count}{dry_run_suffix}\n"
        f"\tReclaimed disk space       : {humanize.naturalsize(perf_counters.reclaimed_space)}{dry_run_suffix}\n"
    )
    logger.info(f"App finished @ {human_readable_interval}")
