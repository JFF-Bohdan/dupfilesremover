import fnmatch
import functools
import hashlib
import itertools
import os
import pathlib
import platform
import typing

from dupfilesremover import consts, data_types

from loguru import logger


def get_file_creation_timestamp(path_to_file: str) -> int | float:
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == "Windows":
        return os.path.getctime(path_to_file)

    stat = os.stat(path_to_file)
    try:
        return stat.st_birthtime
    except AttributeError:
        # We're probably on Linux. No easy way to get creation dates here,
        # so we'll settle for when its content was last modified.
        return stat.st_mtime


def list_files(path: str, recurse: bool = False) -> typing.Generator[data_types.FileInfo, None, None]:
    folder = pathlib.Path(path)

    generator = folder.rglob("*") if recurse else folder.iterdir()

    for item in generator:
        if not item.is_file():
            continue

        yield data_types.FileInfo(
            file_name=str(item.resolve()),
            file_size=item.stat().st_size,
            creation_timestamp=get_file_creation_timestamp(str(item))
        )


def read_file_in_chunks(
        file_object: typing.BinaryIO,
        buffer_size: int = consts.FILE_READ_BUFFER
) -> typing.Generator[bytes, None, None]:
    chunker = functools.partial(file_object.read, buffer_size)
    for chunk in iter(chunker, b""):
        yield chunk


def file_digest(
    file_object: typing.BinaryIO,
    hash_name: str,
    buffer_size: int = consts.FILE_READ_BUFFER,
) -> str:
    hash = hashlib.new(hash_name)
    for chunk in read_file_in_chunks(file_object, buffer_size):
        hash.update(chunk)

    return hash.hexdigest()


def hash_file(
    file_name: str,
    hash_name: str = "sha3_256",
    buffer_size: int = consts.FILE_READ_BUFFER,
) -> str:
    with open(file_name, "rb", buffering=0) as input_file:
        if hasattr(hashlib, "file_digest"):  # pragma: no cover
            return hashlib.file_digest(input_file, hash_name).hexdigest()

        return file_digest(file_object=input_file, hash_name=hash_name, buffer_size=buffer_size)


def remove_files(
    files: list[data_types.FileInfo],
    perf_counters: data_types.PerfCounters,
    dry_run: bool = True
) -> None:
    for file in files:
        logger.info(f"Removing file: {file.file_name}")
        perf_counters.reclaimed_space += file.file_size
        perf_counters.removed_files_count += 1
        if dry_run:
            continue

        os.remove(file.file_name)


def filter_files_by_masks(
        files: typing.Iterable[data_types.FileInfo],
        perf_counters: data_types.PerfCounters,
        masks: list[str] | None = None
) -> typing.Generator[data_types.FileInfo, None, None]:
    """
    Filters files by masks. Returns only files that would have a name that matches any of the masks.

    files: list of file names
    masks: list of mask (Example: ["*.txt", "*.jpg"]
    """
    if not masks:
        yield from files
        return

    for file in files:
        if any((fnmatch.fnmatch(file.file_name, mask) for mask in masks)):
            yield file
            continue

        perf_counters.files_skipped_by_mask += 1


def find_files_in_folders(
        folders: list[str],
        perf_counters: data_types.PerfCounters,
        recurse: bool = False
) -> typing.Generator[data_types.FileInfo, None, None]:
    """
    Returns generator with all file names of all files located in all target folders
    """
    for item in itertools.chain(*[list_files(path, recurse=recurse) for path in folders]):
        perf_counters.total_files_count += 1
        yield item
