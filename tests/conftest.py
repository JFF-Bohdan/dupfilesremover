import pathlib

from consts import TEST_FILES, TEST_FOLDERS

from dupfilesremover import data_types

import pytest


@pytest.fixture
def make_test_folders_on_disk(tmp_path):
    root = pathlib.Path(tmp_path)
    for path in TEST_FOLDERS:
        folder = root / path
        folder.mkdir(exist_ok=False)


@pytest.fixture
def make_test_files_and_folders(tmp_path, make_test_folders_on_disk) -> None:
    root = pathlib.Path(tmp_path)
    for folder, file_name, content, _, in TEST_FILES:
        folder = root / folder
        if not folder.exists():
            folder.mkdir(exist_ok=False)

        file = folder / file_name
        file.write_text(content)


@pytest.fixture
def path_objects_of_test_files(tmp_path) -> list[pathlib.Path]:
    result = []
    root = pathlib.Path(tmp_path)
    for folder, file_name, content, _, in TEST_FILES:
        folder = root / folder
        file = folder / file_name
        result.append(file)

    return result


@pytest.fixture
def file_info_for_test_files(tmp_path) -> list[data_types.FileInfo]:
    result = []

    root = pathlib.Path(tmp_path)
    for folder, file_name, content, hash, in TEST_FILES:
        result.append(
            data_types.FileInfo(
                file_name=str((root / folder / file_name).resolve()),
                file_size=len(content),
                hash=hash,
            )
        )
    return result
