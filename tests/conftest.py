import pathlib

import pytest

from consts import TEST_FOLDERS, TEST_FILES


@pytest.fixture
def test_folders(tmp_path):
    root = pathlib.Path(tmp_path)
    for path in TEST_FOLDERS:
        folder = root / path
        folder.mkdir(exist_ok=False)


@pytest.fixture
def test_files_and_folders(tmp_path, test_folders) -> None:
    root = pathlib.Path(tmp_path)
    for folder, file_name, content, _, in TEST_FILES:
        folder = root / folder
        if not folder.exists():
            folder.mkdir(exist_ok=False)

        file = folder / file_name
        file.write_text(content)
