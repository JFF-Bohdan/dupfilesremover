
import pathlib

from dupfilesremover import data_types, file_system

MANDATORY_FOLDERS = ["folder1", "folder2", "folder3"]

REQUIRED_FILES = [
    (
        "folder1",
        "dot-test.txt",
        "The quick brown fox jumps over the lazy dog.",
        "a80f839cd4f83f6c3dafc87feae470045e4eb0d366397d5c6ce34ba1739f734d",
    ),
    (
        "folder1",
        "dot-test-2.txt",
        "The quick brown fox jumps over the lazy dog.",
        "a80f839cd4f83f6c3dafc87feae470045e4eb0d366397d5c6ce34ba1739f734d",
    ),
    (
        "folder1",
        "test.txt",
        "The quick brown fox jumps over the lazy dog",
        "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04",
    ),
    (
        "folder1",
        "test-2.txt",
        "The quick brown fox jumps over the lazy dog",
        "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04",
    ),

    (
        "folder1/sub-folder",
        "unique_size-1.txt",
        "abc",
        "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532",
    ),
    (
        "folder1/sub-folder",
        "unique_size-2.txt",
        "abcdef",
        "59890c1d183aa279505750422e6384ccb1499c793872d6f31bb3bcaa4bc9f5a5",
    ),

    (
        "folder2",
        "dot-test.txt",
        "The quick brown fox jumps over the lazy dog.",
        "a80f839cd4f83f6c3dafc87feae470045e4eb0d366397d5c6ce34ba1739f734d",
    ),
    (
        "folder2",
        "test.txt",
        "The quick brown fox jumps over the lazy dog",
        "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04",
    ),
]


def make_mandatory_folders(root_folder: pathlib.Path) -> None:
    root = pathlib.Path(root_folder)
    for path in MANDATORY_FOLDERS:
        folder = root / path
        folder.mkdir(exist_ok=False)


def make_test_structure(root_folder: pathlib.Path) -> None:
    # folder, file name, content
    make_mandatory_folders(root_folder)

    root = pathlib.Path(root_folder)
    for folder, file_name, content, _, in REQUIRED_FILES:
        folder = root / folder
        if not folder.exists():
            folder.mkdir(exist_ok=False)

        file = folder / file_name
        file.write_text(content)


def test_supports_non_recursive_search(tmp_path):
    make_test_structure(tmp_path)

    expected_results = {
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "dot-test.txt"),
            file_size=44
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "dot-test-2.txt"),
            file_size=44
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "test.txt"),
            file_size=43
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "test-2.txt"),
            file_size=43
        ),

        data_types.FileInfo(
            file_name=str(tmp_path / "folder2" / "dot-test.txt"),
            file_size=44
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder2" / "test.txt"),
            file_size=43
        ),

    }

    found_items = set()
    for path in MANDATORY_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=False)
            )
        )

    assert expected_results == found_items


def test_supports_recursive_search(tmp_path):
    make_test_structure(tmp_path)

    expected_results = {
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "dot-test.txt"),
            file_size=44
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "dot-test-2.txt"),
            file_size=44
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "test.txt"),
            file_size=43
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "test-2.txt"),
            file_size=43
        ),

        data_types.FileInfo(
            file_name=str(tmp_path / "folder2" / "dot-test.txt"),
            file_size=44
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder2" / "test.txt"),
            file_size=43
        ),

        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "sub-folder" / "unique_size-1.txt"),
            file_size=3
        ),
        data_types.FileInfo(
            file_name=str(tmp_path / "folder1" / "sub-folder" / "unique_size-2.txt"),
            file_size=6
        ),
    }

    found_items = set()
    for path in MANDATORY_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    assert expected_results == found_items


def test_supports_empty_folders_non_recurse(tmp_path):
    make_mandatory_folders(tmp_path)

    found_items = set()
    for path in MANDATORY_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=False)
            )
        )

    assert found_items == set()


def test_supports_empty_folders_recurse(tmp_path):
    make_mandatory_folders(tmp_path)

    found_items = set()
    for path in MANDATORY_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    assert found_items == set()


def test_can_compute_hashes(tmp_path):
    make_test_structure(tmp_path)

    expected_results = {}
    for folder, file_name, content, expected_hash, in REQUIRED_FILES:
        file_name = str(tmp_path / folder / file_name)
        expected_results[file_name] = expected_hash

    found_items = set()
    for path in MANDATORY_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    computed_results = {}
    for item in found_items:
        hash = file_system.hash_file(item.file_name)
        computed_results[item.file_name] = hash

    assert expected_results == computed_results

