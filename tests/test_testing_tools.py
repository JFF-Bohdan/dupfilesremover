import os.path

import consts as test_consts

import pytest


@pytest.mark.order("first")
def test_can_create_test_files(tmp_path, make_test_files_and_folders):
    all_files = set(
        test_consts.FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS +
        test_consts.FILES_EXPECTED_TO_BE_DELETED_WITHOUT_MASKS
    )

    all_files = [
        str((tmp_path / item).resolve()) for item in all_files
    ]
    assert all([os.path.exists(path) for path in all_files])
