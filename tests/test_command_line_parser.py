import consts

from dupfilesremover import command_line_parser


def test_default_format():
    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(args=["--recurse", *consts.TEST_FOLDERS])

    assert args.recurse is True
    assert args.dry_run is False
    assert args.folders == consts.TEST_FOLDERS


def test_supports_dry_run():
    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(args=["--recurse", "--dry-run", *consts.TEST_FOLDERS])

    assert args.recurse is True
    assert args.dry_run is True
    assert args.folders == consts.TEST_FOLDERS


def test_support_mask_sets():
    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(args=["--recurse", "--mask-sets", "images", "--dry-run", *consts.TEST_FOLDERS])

    assert args.recurse is True
    assert args.dry_run is True
    assert args.folders == consts.TEST_FOLDERS
    assert args.mask_sets == "images"
