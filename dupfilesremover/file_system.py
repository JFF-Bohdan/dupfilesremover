import hashlib
import pathlib
import typing

from dupfilesremover import data_types


# TODO: change output to generator
def list_files(path: str, recurse: bool = False) -> typing.Iterable[data_types.FileInfo]:
    folder = pathlib.Path(path)

    generator = folder.rglob("*") if recurse else folder.iterdir()

    for item in generator:
        if not item.is_file():
            continue

        yield data_types.FileInfo(
            file_name=str(item.resolve()),
            file_size=item.stat().st_size
        )


def hash_file(file_name: str) -> str:
    with open(file_name, "rb", buffering=0) as input_file:
        return hashlib.file_digest(input_file, "sha3_256").hexdigest()
