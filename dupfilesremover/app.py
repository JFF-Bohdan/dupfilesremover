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


def find_target_files(
        folders: list[str],
        perf_counters: data_types.PerfCounters,
        recurse: bool = False
) -> typing.Generator[data_types.FileInfo, None, None]:
    for item in itertools.chain(*[file_system.list_files(path, recurse=recurse) for path in folders]):
        perf_counters.total_files_count += 1
        yield item
    # for path in folders:
    #     yield from file_system.list_files(path, recurse=recurse)


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
            logger.info(f"Hash {key} contains only one file {hash_to_files[key][0]}, skipping")
            del hash_to_files[key]
            perf_counters.unique_files_count += 1
            continue

        result[key] = hash_to_files[key]

    return result


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

    weighted_folders = weighting.weight_folders(folders)
    logger.info(f"Weighted folders: {weighted_folders}")

    logger.debug(f"Folders to process: {folders}")

    files = misc.compute_hashes_for_files(
        misc.remove_files_with_unique_size(
            find_target_files(
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
    logger.info(f"Hash to files: {hash_to_files}")

    hash_to_files = filter_out_unique_files(
        hash_to_files,
        perf_counters
    )

    hash_to_files = weighting.vote_and_sort_duplicates(hash_to_files, weighted_folders)
    logger.debug(f"hash_to_files = {hash_to_files}")

    for key, files in hash_to_files.items():
        if len(files) <= 1:
            raise RuntimeError("Error during attempt to delete files")

        logger.debug(f"Processing hash {key}")
        file_to_save = files[0]
        files_to_delete = files[1:]

        logger.info(f"File to save: {file_to_save}")
        logger.info(f"Files to remove: {files_to_delete}")

    human_readable_interval = humanize.precisedelta(
        dt.timedelta(seconds=time.monotonic() - timestamp_begin),
        minimum_unit="microseconds"
    )
    logger.info(
        f"Stats:\n"
        f"\tTotal files count          : {perf_counters.total_files_count}\n"
        f"\tHashed data size           : {perf_counters.hashed_data_size}\n"
        f"\tSkipped due to unique size : {perf_counters.files_skipped_due_to_unique_size}\n"
        f"\tSkipped due to unique hash : {perf_counters.unique_files_count}\n"
    )
    logger.info(f"App finished @ {human_readable_interval}")


# DCIM/folder1 DCIM/folder2 DCIM
# DCIM/folder1 DCIM/folder1