import collections
import pathlib

import consts as test_consts

from dupfilesremover import consts, data_types, exceptions, misc

import helpers

import pytest


def test_can_group_files_by_hash():
    input_data = [
        data_types.FileInfo(
            file_name="foo",
            file_size=3,
            hash="abc",
        ),
        data_types.FileInfo(
            file_name="bar",
            file_size=3,
            hash="abc",
        ),
        data_types.FileInfo(
            file_name="bizz",
            file_size=4,
            hash="abcdef",
        ),
        data_types.FileInfo(
            file_name="bazz",
            file_size=4,
            hash="abcdef",
        ),
        data_types.FileInfo(
            file_name="unique",
            file_size=42,
            hash="foobar",
        ),
    ]
    result = misc.group_files_by_hash(input_data)

    expected_result = {
        "abc": [
            data_types.FileInfo(
                file_name="foo",
                file_size=3,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="bar",
                file_size=3,
                hash="abc",
            ),
        ],
        "abcdef": [
            data_types.FileInfo(
                file_name="bizz",
                file_size=4,
                hash="abcdef",
            ),
            data_types.FileInfo(
                file_name="bazz",
                file_size=4,
                hash="abcdef",
            ),
        ],
        "foobar": [
            data_types.FileInfo(
                file_name="unique",
                file_size=42,
                hash="foobar",
            ),
        ],
    }

    assert result == expected_result


def test_can_filter_out_files_with_unique_hash():
    input_data = {
        "abc": [
            data_types.FileInfo(
                file_name="foo",
                file_size=3,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="bar",
                file_size=3,
                hash="abc",
            ),
        ],
        "abcdef": [
            data_types.FileInfo(
                file_name="bizz",
                file_size=4,
                hash="abcdef",
            ),
            data_types.FileInfo(
                file_name="bazz",
                file_size=4,
                hash="abcdef",
            ),
        ],
        "foobar": [
            data_types.FileInfo(
                file_name="unique",
                file_size=42,
                hash="foobar",
            ),
        ],
        "uniq": [
            data_types.FileInfo(
                file_name="unique-2",
                file_size=45,
                hash="uniq",
            ),
        ],
    }

    perf_counters = data_types.PerfCounters()
    result = misc.filter_out_unique_files(collections.defaultdict(list, input_data), perf_counters)
    expected_result = {
        "abc": [
            data_types.FileInfo(
                file_name="foo",
                file_size=3,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="bar",
                file_size=3,
                hash="abc",
            ),
        ],
        "abcdef": [
            data_types.FileInfo(
                file_name="bizz",
                file_size=4,
                hash="abcdef",
            ),
            data_types.FileInfo(
                file_name="bazz",
                file_size=4,
                hash="abcdef",
            ),
        ],
    }
    assert result == expected_result
    assert perf_counters.files_skipped_due_to_unique_hash == 2


def test_compute_hashes_for_files(
        make_test_files_and_folders,
        path_objects_of_test_files,
        file_info_for_test_files
):
    files_to_calculate = helpers.convert_path_objects_into_file_object(path_objects_of_test_files)

    perf_counters = data_types.PerfCounters()
    hashed_files = misc.compute_hashes_for_files(
        files=files_to_calculate,
        perf_counters=perf_counters,
    )
    actual_hashes = {
        item.file_name: item.hash for item in hashed_files
    }
    expected_hashes = {
        item.file_name: item.hash for item in file_info_for_test_files
    }

    assert actual_hashes == expected_hashes


def test_support_images_mask():
    assert misc.is_mask_set_supported("images") is True


def test_can_detect_unsupported_mask():
    assert misc.is_mask_set_supported("does_not_exists") is False


def test_can_check_if_folder_exists(tmp_path, make_test_folders_on_disk):
    for folder in test_consts.TEST_FOLDERS:
        assert misc.is_folder_exists(tmp_path / folder) is True

    assert misc.is_folder_exists("does_not_exists") is False


def test_can_validate_folders(tmp_path, make_test_folders_on_disk):
    folders = [str((tmp_path / folder).resolve()) for folder in test_consts.TEST_FOLDERS]
    misc.validate_folders(folders)


def test_raises_exception_when_validating_folder_that_doesnt_exists():
    with pytest.raises(exceptions.FolderDoesNotExistsError):
        misc.validate_folders(["does_not_exists"])


def test_can_normalize_folders(tmp_path, make_test_folders_on_disk):
    folders = [str(pathlib.Path(folder).resolve()) for folder in test_consts.TEST_FOLDERS]
    result = misc.normalize_folders(folders)

    assert result == folders


def test_can_flatten_images_mask():
    result = misc.get_flat_masks("images")
    expected_result = consts.IMAGES

    assert result == expected_result


def test_raises_exception_on_unknown_images_mask():
    with pytest.raises(exceptions.FileMaskIsNotSupportedError) as e:
        misc.get_flat_masks("does_not_exists")
        assert e.mask == "does_not_exists"
