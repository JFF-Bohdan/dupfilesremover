import collections
import os
import typing
import tqdm

from loguru import logger
from dupfilesremover import tqdm_to_logger

from dupfilesremover import data_types, exceptions, file_system


def is_folder_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


def validate_folders(folders: list[str]) -> None:
    for path in folders:
        if not is_folder_exists(path):
            raise exceptions.FolderDoesNotExistsError(f"Folder {path} does not exists")


def normalize_folders(folders: list[str]) -> list[str]:
    # replace("\\", "/")
    return [os.path.abspath(os.path.normpath(path)) for path in folders]


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
