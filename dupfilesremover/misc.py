import collections
import os
import pathlib
import typing

from dupfilesremover import consts, data_types, exceptions, file_system, tqdm_to_logger

from loguru import logger

import tqdm


def is_mask_set_supported(mask_set_name: str) -> bool:
    return mask_set_name in consts.SUPPORTED_MASKS_SETS


def is_folder_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


def validate_folders(folders: list[str]) -> None:
    for path in folders:
        if is_folder_exists(path):
            continue

        raise exceptions.FolderDoesNotExistsError(f"Folder {path} does not exists")


def normalize_folders(folders: list[str]) -> list[str]:
    return [str(pathlib.Path(path).resolve()) for path in folders]


def remove_files_with_unique_size(
        files: typing.Iterable[data_types.FileInfo],
        perf_counters: data_types.PerfCounters
) -> typing.Generator[data_types.FileInfo, None, None]:
    temp_buffer: collections.defaultdict[int, list[data_types.FileInfo]] = collections.defaultdict(list)
    times_seen: collections.Counter[int, int] = collections.Counter()

    for file in files:
        times_seen.update({file.file_size: 1})
        if times_seen[file.file_size] > 1:
            yield file

            if file.file_size in temp_buffer:
                yield from temp_buffer[file.file_size]
                del temp_buffer[file.file_size]

            continue

        temp_buffer[file.file_size].append(file)

    for file_size, files in temp_buffer.items():
        if times_seen[file_size] == 1:
            perf_counters.files_skipped_due_to_unique_size += 1
            continue

        raise RuntimeError("Error filter out files with unique file sizes")  # pragma: no cover


def compute_hashes_for_files(
    files: typing.Iterable[data_types.FileInfo],
    perf_counters: data_types.PerfCounters,
) -> typing.Generator[data_types.FileInfo, None, None]:
    logger.info("Computing hashes...")
    # We need to materialize list to be able to show progress bar
    files = list(files)

    tqdm_out = tqdm_to_logger.TqdmToLogger(logger)
    generator = tqdm.tqdm(
        files,
        file=tqdm_out,
        desc="Files processed",
        mininterval=10,
        maxinterval=30
    )

    for file in generator:
        perf_counters.hashed_data_size += file.file_size
        yield data_types.FileInfo(
            file_name=file.file_name,
            file_size=file.file_size,
            hash=file_system.hash_file(file.file_name),
            creation_timestamp=file.creation_timestamp,
        )


def group_files_by_hash(
        files: typing.Iterable[data_types.FileInfo]
) -> collections.defaultdict[str, list[data_types.FileInfo]]:
    """
    Groups files by hash. Output will be a dictionary where key is a hash
    and value is a list of files with such hash
    """
    result: collections.defaultdict[str, list[data_types.FileInfo]] = collections.defaultdict(list)
    for file in files:
        result[file.hash].append(file)

    return result


def filter_out_unique_files(
        hash_to_files: collections.defaultdict[str, list[data_types.FileInfo]],
        perf_counters: data_types.PerfCounters,
) -> dict[str, list[data_types.FileInfo]]:
    """
    Removes files with unique hash.

    Input is a dictionary where key is a hash and value is a list of files with a such hash.
    As a result, output will contain only such hashes where more than one file has such hash.
    """
    result: dict[str, list[data_types.FileInfo]] = {}

    keys = list(hash_to_files.keys())
    for key in keys:
        if len(hash_to_files[key]) == 1:
            logger.debug(f"Hash {key} contains only one file {hash_to_files[key][0]}, skipping")
            perf_counters.files_skipped_due_to_unique_hash += 1
            continue

        result[key] = hash_to_files[key]

    return result
