import hashlib
import os
import pathlib

import consts as test_consts

from dupfilesremover import consts, data_types, file_system

import helpers


def test_supports_empty_filter():
    files = helpers.convert_file_name_to_file_object(["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg"])

    perf_counters = data_types.PerfCounters()
    result = list(file_system.filter_files_by_masks(files, perf_counters, None))
    assert result == files
    assert perf_counters.files_skipped_by_mask == 0


def test_filter_by_mask():
    files = helpers.convert_file_name_to_file_object(
        ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg", "text-file.txt"]
    )
    expected_result = helpers.convert_file_name_to_file_object(["some-image.jpeg", "some-image.jpg", "text-file.txt"])

    perf_counters = data_types.PerfCounters()
    result = list(file_system.filter_files_by_masks(files, perf_counters, ["*.jpg", "*.jpeg", "*.txt"]))
    assert result == expected_result
    assert perf_counters.files_skipped_by_mask == 2


def test_can_filter_for_images():
    files = helpers.convert_file_name_to_file_object(
        ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg", "text-file.txt"]
    )
    expected_result = helpers.convert_file_name_to_file_object(["some-image.jpeg", "some-image.jpg"])

    perf_counters = data_types.PerfCounters()
    result = list(file_system.filter_files_by_masks(files, perf_counters, consts.IMAGES))
    assert result == expected_result
    assert perf_counters.files_skipped_by_mask == 3


def test_can_find_files_in_list_of_folders(tmp_path, make_test_files_and_folders, mocker):
    mocker.patch("dupfilesremover.file_system.get_file_creation_timestamp", return_value=0)

    perf_counters = data_types.PerfCounters()
    result = file_system.find_files_in_folders(
        folders=[str(pathlib.Path(tmp_path) / folder) for folder in test_consts.TEST_FOLDERS],
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


def test_will_skip_deletion_of_files_in_dry_run_mocked(
    make_test_files_and_folders,
    path_objects_of_test_files,
    mocker,
):
    mocked_os_remove = mocker.patch("os.remove")

    perf_counters = data_types.PerfCounters()

    file_info_list = helpers.convert_path_objects_into_file_object(path_objects_of_test_files)
    expected_reclaimed_space = sum(item.file_size for item in file_info_list)

    file_system.remove_files(
        files=file_info_list,
        perf_counters=perf_counters,
        dry_run=True
    )

    # assert all(file.exists() for file in path_objects_of_test_files)
    assert perf_counters.removed_files_count == len(file_info_list)
    assert perf_counters.reclaimed_space == expected_reclaimed_space
    mocked_os_remove.assert_not_called()


def test_remove_required_files_mocked(
    make_test_files_and_folders,
    path_objects_of_test_files,
    mocker,
):
    mocked_os_remove = mocker.patch("os.remove")
    perf_counters = data_types.PerfCounters()

    files_to_delete = helpers.convert_path_objects_into_file_object(
        [item for index, item in enumerate(path_objects_of_test_files) if index % 2 == 1]
    )
    expected_reclaimed_space = sum(item.file_size for item in files_to_delete)
    expected_calls = [
        mocker.call(item.file_name) for item in files_to_delete
    ]

    files_to_keep = helpers.convert_path_objects_into_file_object(
        [item for index, item in enumerate(path_objects_of_test_files) if index % 2 == 0]
    )

    assert set(files_to_keep) & set(files_to_delete) == set()

    file_system.remove_files(
        files=files_to_delete,
        perf_counters=perf_counters,
        dry_run=False
    )

    # assert all(os.path.exists(file.file_name) for file in files_to_keep)
    # assert all(not os.path.exists(file.file_name) for file in files_to_delete)

    assert perf_counters.removed_files_count == len(files_to_delete)
    assert perf_counters.reclaimed_space == expected_reclaimed_space
    mocked_os_remove.assert_has_calls(
        expected_calls,
    )


def test_remove_required_files_non_mocked(
    make_test_files_and_folders,
    path_objects_of_test_files,
):
    perf_counters = data_types.PerfCounters()

    files_to_delete = helpers.convert_path_objects_into_file_object(
        [item for index, item in enumerate(path_objects_of_test_files) if index % 2 == 1]
    )
    expected_reclaimed_space = sum(item.file_size for item in files_to_delete)

    files_to_keep = helpers.convert_path_objects_into_file_object(
        [item for index, item in enumerate(path_objects_of_test_files) if index % 2 == 0]
    )

    assert set(files_to_keep) & set(files_to_delete) == set()

    file_system.remove_files(
        files=files_to_delete,
        perf_counters=perf_counters,
        dry_run=False
    )

    assert all(os.path.exists(file.file_name) for file in files_to_keep)
    assert all(not os.path.exists(file.file_name) for file in files_to_delete)
    assert perf_counters.removed_files_count == len(files_to_delete)
    assert perf_counters.reclaimed_space == expected_reclaimed_space


def test_can_get_file_creation_on_windows(
    make_test_folders_on_disk,
    file_info_for_test_files,
    mocker
):
    files = file_info_for_test_files
    assert files

    mocker.patch("platform.system", return_value="Windows")
    mocker.patch("os.path.getctime", return_value=42)
    result = file_system.get_file_creation_timestamp(files[0].file_name)
    assert result == 42


def test_can_get_file_creation_on_linux_new_python(
    make_test_folders_on_disk,
    file_info_for_test_files,
    mocker
):
    files = file_info_for_test_files
    assert files

    mocked_stat = mocker.MagicMock()
    mocked_stat.st_birthtime = 123

    mocker.patch("platform.system", return_value="Linux")
    mocker.patch("os.stat", return_value=mocked_stat)
    result = file_system.get_file_creation_timestamp(files[0].file_name)
    assert result == 123
    mocked_stat.st_mtime.assert_not_called()


def test_can_get_file_creation_on_linux_old_python(
    make_test_folders_on_disk,
    file_info_for_test_files,
    mocker
):
    files = file_info_for_test_files
    assert files

    mocked_stat = mocker.Mock(spec=[])
    no_attribute = mocker.PropertyMock(side_effect=AttributeError())
    type(mocked_stat).st_birthtime = no_attribute
    type(mocked_stat).st_mtime = mocker.PropertyMock(return_value=321)

    mocker.patch("platform.system", return_value="Linux")
    mocker.patch("os.stat", return_value=mocked_stat)

    result = file_system.get_file_creation_timestamp(files[0].file_name)
    assert result == 321


def test_can_read_file_in_chunks(tmp_path, make_test_files_and_folders):
    with open(tmp_path / "folder1/dot-test.txt", "rb") as input_file:
        result = list(file_system.read_file_in_chunks(input_file, 10))

    result = [chunk.decode("utf-8") for chunk in result]
    expected_result = [
        "The quick ",
        "brown fox ",
        "jumps over",
        " the lazy ",
        "dog.",
    ]
    assert result == expected_result
    assert "".join(result) == "The quick brown fox jumps over the lazy dog."


def test_can_compute_hashes(tmp_path, make_test_files_and_folders):
    found_items = set()
    for path in test_consts.TEST_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    computed_results = {}
    for item in found_items:
        hash = file_system.hash_file(item.file_name)
        computed_results[item.file_name] = hash

    expected_results = {}
    for folder, file_name, content, expected_hash, in test_consts.TEST_FILES:
        file_name = str(tmp_path / folder / file_name)
        expected_results[file_name] = expected_hash

    assert expected_results == computed_results


def test_can_compute_hashes_no_build_in_file_hasher(tmp_path, make_test_files_and_folders, monkeypatch):
    monkeypatch.delattr(hashlib, "file_digest")

    found_items = set()
    for path in test_consts.TEST_FOLDERS:
        found_items.update(
            list(
                file_system.list_files(str(tmp_path / path), recurse=True)
            )
        )

    computed_results = {}
    for item in found_items:
        hash = file_system.hash_file(item.file_name)
        computed_results[item.file_name] = hash

    expected_results = {}
    for folder, file_name, content, expected_hash, in test_consts.TEST_FILES:
        file_name = str(tmp_path / folder / file_name)
        expected_results[file_name] = expected_hash

    assert expected_results == computed_results
