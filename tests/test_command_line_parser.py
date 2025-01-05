from dupfilesremover import command_line_parser


def test_default_format():
    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(args=["--recurse", "data1", "data2"])

    assert args.recurse is True
    assert args.dry_run is False
    assert args.folders == ["data1", "data2"]


def test_supports_dry_run():
    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(args=["--recurse", "--dry-run", "data1", "data2"])

    assert args.recurse is True
    assert args.dry_run is True
    assert args.folders == ["data1", "data2"]


def test_support_mask_sets():
    parser = command_line_parser.create_command_line_parser()
    args = parser.parse_args(args=["--recurse", "--mask-sets", "images", "--dry-run", "data1", "data2"])

    assert args.recurse is True
    assert args.dry_run is True
    assert args.folders == ["data1", "data2"]
    assert args.mask_sets == "images"
