import configargparse

from dupfilesremover import __version__


def create_command_line_parser(auto_env_var_prefix: str | None = None) -> configargparse.ArgParser:
    parser = configargparse.ArgParser(
        auto_env_var_prefix=auto_env_var_prefix
    )
    parser.add_argument(
        "--config",
        metavar="FILE",
        is_config_file=True,
        help="Path to configuration file",
        required=False
    )
    parser.add_argument(
        "--recurse",
        "-r",
        action="store_true",
        default=False,
        help="Recursive analysis of provided directories"
    )
    parser.add_argument(
        "--dry-run",
        "-d",
        action="store_true",
        default=False,
        help="Dry-run, no actual deletion will be performed. "
             "Will just print list of files to be deleted on the console"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Verbose mode, will print debug messages on the console"
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--mask-sets",
        "-s",
        action="store"
    )
    parser.add_argument(
        "folders",
        nargs="*",
        type=str,
        help="Folders that need to be processed"
    )

    return parser
