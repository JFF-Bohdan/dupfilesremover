import consts as test_consts

from dupfilesremover import app

import pytest


def test_end_to_end_in_dry_run_mode(tmp_path, make_test_files_and_folders, mocker):
    mocked_os_remove = mocker.patch("os.remove")

    folders = [str((tmp_path / folder).resolve()) for folder in test_consts.TEST_FOLDERS]

    args = [
        "--dry-run",
        "--recurse",
        *folders
    ]
    app.main(args)
    mocked_os_remove.assert_not_called()


def test_end_to_end_in_normal_mode(tmp_path, make_test_files_and_folders, mocker):
    mocked_os_remove = mocker.patch("os.remove")

    folders = [str((tmp_path / folder).resolve()) for folder in test_consts.TEST_FOLDERS]

    args = [
        "--recurse",
        *folders
    ]

    app.main(args)
    expected_calls = [
        mocker.call(str((tmp_path / file).resolve()))
        for file in test_consts.FILES_EXPECTED_TO_BE_DELETED_WITHOUT_MASKS
    ]

    mocked_os_remove.assert_has_calls(
        expected_calls,
        any_order=True
    )


def test_exits_on_unknown_folder(mocker):
    mocker.patch("os.remove")

    args = [
        "--recurse",
        "does_not_exists"
    ]

    with pytest.raises(SystemExit):
        app.main(args)


def test_exits_on_unknown_mask(mocker, tmp_path, make_test_folders_on_disk):
    mocker.patch("os.remove")

    folder = str((tmp_path / test_consts.TEST_FOLDERS[0]).resolve())
    args = [
        "--recurse",
        "--mask-sets",
        "does_not_exists",
        folder,
    ]

    with pytest.raises(SystemExit):
        app.main(args)
