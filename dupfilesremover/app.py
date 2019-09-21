import argparse
import configparser
import os

from dupfilesremover.implementation.duplicate_files_remover import DuplicateImagesRemover
from dupfilesremover.version import __version__


DEFAULT_CONFIG_RELATIVE_NAME = "../config/config.ini"
NAMED_FILE_MASKS_GROUP_NAME = "predefined_masks"


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{{path}} is not a valid path".format(path=path))


def get_cli_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--recurse", "-r", action="store_true", default=False)
    parser.add_argument("--version", "-v", action="version", version="%(prog)s {}".format(__version__))
    parser.add_argument("--masks_set_name", "-m", action="store")
    parser.add_argument("--config", "-c", type=argparse.FileType("r"))
    parser.add_argument("directories", nargs="*", type=dir_path)

    return parser.parse_args()


class DuplicateImagesRemoverApplication(object):
    def __init__(self, logger):
        self.logger = logger

    def run(self):
        args = get_cli_args()
        self.logger.info("target folders: {}".format(args.directories))

        acceptable_extensions = None
        if args.masks_set_name:
            acceptable_extensions = self.get_acceptable_extensions(args)
            if acceptable_extensions is None:
                return

            self.logger.debug("acceptable_extensions: {}".format(acceptable_extensions))

        worker = DuplicateImagesRemover(
            logger=self.logger,
            target_folders=args.directories,
            recurse=args.recurse,
            acceptable_extensions=acceptable_extensions
        )
        worker.remove_duplicate_images()

    def get_acceptable_extensions(self, args):
        config_file_name = args.config
        if not config_file_name:
            config_file_name = DEFAULT_CONFIG_RELATIVE_NAME
            src_path = os.path.abspath(os.path.dirname(__file__))
            assert os.path.exists(src_path)
            self.logger.debug("src_path: '{}'".format(src_path))

            config_file_name = os.path.join(src_path, config_file_name)
            config_file_name = os.path.abspath(config_file_name)
            config_file_name = os.path.normpath(config_file_name)
            assert os.path.exists(config_file_name)
        else:
            config_file_name = os.path.abspath(config_file_name)
            config_file_name = os.path.normpath(config_file_name)

        if not os.path.exists(config_file_name):
            self.logger.error("configuration file does't exists, file name: '{}'".format(config_file_name))
            return None

        return self.read_masks_for_name_from_config_file(config_file_name, args.masks_set_name)

    @staticmethod
    def read_masks_for_name_from_config_file(config_file_name, named_mask_name, encoding="utf-8"):
        config = configparser.RawConfigParser()
        config.read(config_file_name, encoding)
        mask_extensions = config.get(NAMED_FILE_MASKS_GROUP_NAME, named_mask_name)

        mask_extensions = str(mask_extensions).strip().split(",")
        return [str(item).strip() for item in mask_extensions if str(item).strip()]
