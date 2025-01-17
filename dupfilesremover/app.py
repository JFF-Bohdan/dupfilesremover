import datetime as dt
import sys
import time

from dupfilesremover import command_line_parser, consts, data_types, exceptions, file_system, misc, weighting

import humanize

from loguru import logger


def main(command_line_args: list[str] | None = None):
    timestamp_begin = time.monotonic()
    perf_counters = data_types.PerfCounters()

    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")

    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(command_line_args)

    folders = misc.normalize_folders(args.folders)
    try:
        misc.validate_folders(args.folders)
    except exceptions.FolderDoesNotExistsError as e:
        logger.error(e)
        sys.exit(1)

    try:
        files_masks = misc.get_flat_masks(args.mask_sets) if args.mask_sets else None
    except exceptions.FileMaskIsNotSupportedError as e:
        logger.error(
            f"Mask set {e.mask} is not supported. Supported masks are: "
            f"{list(consts.SUPPORTED_MASKS_SETS.keys())}"
        )
        sys.exit(1)

    weighted_folders = weighting.weight_folders(folders)
    logger.debug(f"Weighted folders: {weighted_folders}")

    debug_message = "\n\t".join(folders)
    logger.info(f"Folders to process:\n\t{debug_message}")

    gen_files = misc.compute_hashes_for_files(
        misc.remove_duplicate_file_names(
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
        ),
        perf_counters
    )
    files = list(gen_files)
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
        if len(files) <= 1:  # pragma: no cover
            raise RuntimeError("Error during attempt to delete files")

        logger.info(f"For hash {key}")

        file_to_save = files[0]
        files_to_delete = files[1:]

        logger.info(f"File to keep: {file_to_save.file_name}")

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
        f"\tTotal files count             : {perf_counters.total_files_count}\n"
        f"\tSkipped by mask               : {perf_counters.files_skipped_by_mask}\n"
        f"\tHashed data size              : {humanize.naturalsize(perf_counters.hashed_data_size)}\n"
        f"\tSkipped due to unique size    : {perf_counters.files_skipped_due_to_unique_size}\n"
        f"\tSkipped due to duplicate name : {perf_counters.files_skipped_by_duplicate_name}\n"
        f"\tSkipped due to unique hash    : {perf_counters.files_skipped_due_to_unique_hash}\n"
        f"\tRemoved files count           : {perf_counters.removed_files_count}{dry_run_suffix}\n"
        f"\tReclaimed disk space          : {humanize.naturalsize(perf_counters.reclaimed_space)}{dry_run_suffix}\n"
    )
    logger.info(f"App finished @ {human_readable_interval}")
