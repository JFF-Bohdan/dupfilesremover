import os.path

import consts as test_consts

from dupfilesremover import app

import pytest


@pytest.mark.order("last")
def test_end_to_end_exec_mode(tmp_path, make_test_files_and_folders):
    folders = [str((tmp_path / folder).resolve()) for folder in test_consts.TEST_FOLDERS]

    args = [
        "--recurse",
        *folders
    ]
    app.main(args)

    files_to_remain = [
        str((tmp_path / item).resolve())
        for item in test_consts.FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS
    ]
    assert all([os.path.exists(path) for path in files_to_remain])

    files_to_be_deleted = [
        str((tmp_path / item).resolve())
        for item in test_consts.FILES_EXPECTED_TO_BE_DELETED_WITHOUT_MASKS
    ]
    assert all([not os.path.exists(path) for path in files_to_be_deleted])


@pytest.mark.order("last")
def test_end_to_end_exec_mode_with_root_folder(tmp_path, make_test_files_and_folders):
    folders = [str((tmp_path / folder).resolve()) for folder in test_consts.TEST_FOLDERS]

    args = [
        "--recurse",
        *folders,
        str(tmp_path.resolve())
    ]
    app.main(args)

    files_to_remain = [
        str((tmp_path / item).resolve())
        for item in test_consts.FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS
    ]
    assert all([os.path.exists(path) for path in files_to_remain])

    files_to_be_deleted = [
        str((tmp_path / item).resolve())
        for item in test_consts.FILES_EXPECTED_TO_BE_DELETED_WITHOUT_MASKS
    ]
    assert all([not os.path.exists(path) for path in files_to_be_deleted])
