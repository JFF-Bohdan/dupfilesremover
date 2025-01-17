from dupfilesremover import data_types, weighting

import pytest


def test_weight_folders():
    test_data = ["folder-1", "folder-2", "folder-3"]
    expected_result = {
        "folder-1": 0,
        "folder-2": 1,
        "folder-3": 2
    }
    result = weighting.weight_folders(test_data)
    assert result == expected_result


def test_calculate_weights_for_files():
    weighted_folders = {
        "folder1": 0,
        "folder2": 1,
        "folder3": 2,
    }
    files = {
        "abc": [
            data_types.FileInfo(
                file_name="folder1/sub-folder/file-1",
                file_size=1,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="folder2/file-1",
                file_size=1,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="folder1/file-1",
                file_size=1,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="folder1/file-1-copy",
                file_size=1,
                hash="abc",
            ),
        ],
        "def": [
            data_types.FileInfo(
                file_name="folder3/file-1",
                file_size=2,
                hash="def",
            ),
            data_types.FileInfo(
                file_name="folder1/file-1",
                file_size=1,
                hash="def",
                creation_timestamp=1,
            ),
            data_types.FileInfo(
                file_name="folder1/file-2",
                file_size=1,
                hash="def",
                creation_timestamp=2,
            ),
        ]
    }
    expected_result = {
        "abc": [
            "folder1/file-1",
            "folder1/file-1-copy",
            "folder1/sub-folder/file-1",
            "folder2/file-1",
        ],
        "def": [
            "folder1/file-1",
            "folder1/file-2",
            "folder3/file-1",
        ]

    }
    result = weighting.vote_and_sort_duplicates(
        files,
        weighted_folders,
    )

    def extract_only_names(data: list[data_types.FileInfo]) -> list[str]:
        return [item.file_name for item in data]

    result = {key: extract_only_names(value) for key, value in result.items()}
    assert result == expected_result


def test_raises_exception_when_wrong_file_is_found():
    weighted_folders = {
        "folder1": 0,
        "folder2": 1,
        "folder3": 2,
    }
    files = {
        "abc": [
            data_types.FileInfo(
                file_name="ome/sub-folder/file-1",
                file_size=1,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="alien_folder/file-1",
                file_size=1,
                hash="abc",
            ),
        ],
    }
    with pytest.raises(RuntimeError):
        _ = weighting.vote_and_sort_duplicates(
            files,
            weighted_folders,
        )
