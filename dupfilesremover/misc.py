import collections
import os
import typing

from dupfilesremover import data_types, exceptions, file_system


def is_folder_exists(path: str) -> bool:
    return os.path.exists(path) and os.path.isdir(path)


def validate_folders(folders: list[str]) -> None:
    for path in folders:
        if not is_folder_exists(path):
            raise exceptions.FolderDoesNotExistsError(f"Folder {path} does not exists")


def normalize_folders(folders: list[str]) -> list[str]:
    return [os.path.abspath(os.path.normpath(path)).replace("\\", "/") for path in folders]


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
        files: typing.Iterable[data_types.FileInfo]
) -> typing.Generator[data_types.FileInfo, None, None]:
    for file in files:
        yield data_types.FileInfo(
            file_name=file.file_name,
            file_size=file.file_size,
            hast=file_system.hash_file(file.file_name)
        )
