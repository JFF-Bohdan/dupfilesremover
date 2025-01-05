import pathlib

from consts import TEST_FOLDERS

from dupfilesremover import consts, data_types, file_system


def convert_file_name_to_file_object(files: list[str]) -> list[data_types.FileInfo]:
    return [data_types.FileInfo(file_name=item, file_size=1) for item in files]


def test_supports_empty_filter():
    files = convert_file_name_to_file_object(["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg"])

    perf_counters = data_types.PerfCounters()
    result = list(file_system.filter_files_by_masks(files, perf_counters, None))
    assert result == files
    assert perf_counters.files_skipped_by_mask == 0


def test_filter_by_mask():
    files = convert_file_name_to_file_object(
        ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg", "text-file.txt"]
    )
    expected_result = convert_file_name_to_file_object(["some-image.jpeg", "some-image.jpg", "text-file.txt"])

    perf_counters = data_types.PerfCounters()
    result = list(file_system.filter_files_by_masks(files, perf_counters, ["*.jpg", "*.jpeg", "*.txt"]))
    assert result == expected_result
    assert perf_counters.files_skipped_by_mask == 2


def test_can_filter_for_images():
    files = convert_file_name_to_file_object(
        ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg", "text-file.txt"]
    )
    expected_result = convert_file_name_to_file_object(["some-image.jpeg", "some-image.jpg"])

    perf_counters = data_types.PerfCounters()
    result = list(file_system.filter_files_by_masks(files, perf_counters, consts.IMAGES))
    assert result == expected_result
    assert perf_counters.files_skipped_by_mask == 3


def test_can_find_files_in_list_of_folders(tmp_path, test_files_and_folders, mocker):
    mocker.patch("dupfilesremover.file_system.get_file_creation_timestamp", return_value=0)

    perf_counters = data_types.PerfCounters()
    result = file_system.find_files_in_folders(
        folders=[str(pathlib.Path(tmp_path) / folder) for folder in TEST_FOLDERS],
        perf_counters=perf_counters,
        recurse=True,
    )
    result = set(result)

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
            file_name=str(tmp_path / "folder1/sub-folder/unique_size-2.txt"),
            file_size=6
        ),

        data_types.FileInfo(
            file_name=str(tmp_path / "folder1/sub-folder/unique_size-1.txt"),
            file_size=3
        ),
    }

    assert result == expected_results
    assert perf_counters.total_files_count == len(expected_results)
