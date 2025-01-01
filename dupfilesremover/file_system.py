import os
import platform
import hashlib
import pathlib
import typing

from dupfilesremover import data_types


def creation_timestamp(path_to_file: str) -> int | float:
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


# TODO: change output to generator
def list_files(path: str, recurse: bool = False) -> typing.Iterable[data_types.FileInfo]:
    folder = pathlib.Path(path)

    generator = folder.rglob("*") if recurse else folder.iterdir()

    for item in generator:
        if not item.is_file():
            continue

        yield data_types.FileInfo(
            file_name=str(item.resolve()),
            file_size=item.stat().st_size,
            creation_timestamp=creation_timestamp(str(item))
        )


def hash_file(file_name: str) -> str:
    with open(file_name, "rb", buffering=0) as input_file:
        return hashlib.file_digest(input_file, "sha3_256").hexdigest()
