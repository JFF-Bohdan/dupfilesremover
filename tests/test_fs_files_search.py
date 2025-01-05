from consts import TEST_FILES, TEST_FOLDERS

from dupfilesremover import data_types, file_system


def test_supports_non_recursive_search(tmp_path, mocker, test_files_and_folders):
    mocker.patch("dupfilesremover.file_system.get_file_creation_timestamp", return_value=0)

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
    for path in TEST_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=False)
            )
        )

    assert expected_results == found_items


def test_supports_recursive_search(tmp_path, mocker, test_files_and_folders):
    mocker.patch("dupfilesremover.file_system.get_file_creation_timestamp", return_value=0)

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
    for path in TEST_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    assert expected_results == found_items


def test_supports_empty_folders_non_recurse(tmp_path, test_folders):
    # make_mandatory_folders(tmp_path)

    found_items = set()
    for path in TEST_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=False)
            )
        )

    assert found_items == set()


def test_supports_empty_folders_recurse(tmp_path, test_folders):
    found_items = set()
    for path in TEST_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    assert found_items == set()


def test_can_compute_hashes(tmp_path, test_files_and_folders):
    expected_results = {}
    for folder, file_name, content, expected_hash, in TEST_FILES:
        file_name = str(tmp_path / folder / file_name)
        expected_results[file_name] = expected_hash

    found_items = set()
    for path in TEST_FOLDERS:
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
