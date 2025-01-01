import datetime
import os.path
import sys
import time
import datetime as dt

import humanize

from loguru import logger


from dupfilesremover import command_line_parser

from dupfilesremover import misc, exceptions, file_system, data_types


import dataclasses
import pathlib
import typing

import itertools


# TODO: change to generator
def find_target_files(folders: list[str], recurse: bool = False) -> typing.Iterable[data_types.FileInfo]:
    return itertools.chain(*[file_system.list_files(path, recurse=recurse) for path in folders])
    # for path in folders:
    #     yield from file_system.list_files(path, recurse=recurse)


def main():
    perf_counters = data_types.PerfCounters()

    timestamp_begin = time.monotonic()
    logger.remove()
    logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")

    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args()

    try:
        misc.validate_folders(args.folders)
    except exceptions.FolderDoesNotExistsError as e:
        logger.error(e)
        sys.exit(1)

    folders = misc.normalize_folders(args.folders)
    logger.debug(f"Folders to process: {folders}")

    files = misc.compute_hashes_for_files(
        find_target_files(folders, recurse=args.recurse)
    )
    files = list(files)
    num_files = len(files)

    to_print = "\n\t".join([str(item) for item in files])
    logger.debug(f"Files ({num_files}):\n\t{to_print}")

    files = list(misc.remove_files_with_unique_size(files, perf_counters))
    num_files = len(files)
    to_print = "\n\t".join([str(item) for item in files])
    logger.debug(f"Non unique files by file size ({num_files}):\n\t{to_print}")

    human_readable_interval = humanize.precisedelta(
        dt.timedelta(seconds=time.monotonic() - timestamp_begin),
        minimum_unit="microseconds"
    )
    logger.info(f"App finished @ {human_readable_interval}")
