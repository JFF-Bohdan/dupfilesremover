import fnmatch
import hashlib
import os
from collections import Counter, defaultdict, namedtuple

DEFAULT_READ_FILE_BLOCKSIZE = 65536

InitialRawInputData = namedtuple("InitialRawInputData", ["initial_folder_index", "file_name", "file_size"])
HashedFileData = namedtuple(
    "HashedFileData",
    ["initial_folder_index", "file_name", "file_size", "base_file_name", "hash"]
)


class DuplicateImagesRemover(object):
    def __init__(self, target_folders, recurse, logger, acceptable_extensions=None):
        self.logger = logger
        self._target_folders = target_folders
        self._recurse = recurse
        self._acceptable_extensions = acceptable_extensions

    def remove_duplicate_images(self):
        raw_input_data = list()
        for folder_index, target_folder in enumerate(self._target_folders):
            raw_input_data.extend(self._gather_file_names(folder_index, target_folder))

        self.logger.debug("raw_input_data:\n{}".format(raw_input_data))

        raw_input_data = self._filter_for_non_unique_filesize(raw_input_data)
        self.logger.debug("raw_input_data (filtered):\n{}".format(raw_input_data))

        hashes = self._calculate_hashes(raw_input_data)
        self.logger.debug("hashes: {}".format(hashes))

        self.logger.debug("removing unique hashes")
        for key in list(hashes.keys()):
            if len(hashes[key]) < 2:
                del hashes[key]

        if not hashes:
            self.logger.info("nothing to remove")
            return

        self.logger.debug("candidates hashes: {}".format(hashes))
        for key, value in hashes.items():
            base_names = [item.base_file_name for item in value]
            self.logger.info("want remove for hash '{}':\n\t{}".format(key, "\n\t".join(base_names)))
            self._remove_files_with_duplicate_hashes(key, value)

    def _gather_file_names(self, folder_index, folder_name):
        target_items = list()
        filenames = os.listdir(folder_name)

        for filename in filenames:
            abs_name = os.path.join(folder_name, filename)
            abs_name = os.path.abspath(abs_name)

            if os.path.isdir(abs_name):
                if not self._recurse:
                    continue

                target_items.extend(self._gather_file_names(folder_index, abs_name))
                continue

            if not self._is_matching_to_valid_extensions(filename):
                self.logger.debug("'{}' not matching masks".format(filename))
                continue

            target_items.append(
                InitialRawInputData(
                    initial_folder_index=folder_index,
                    file_name=abs_name,
                    file_size=os.path.getsize(abs_name)
                )
            )

        return target_items

    def _filter_for_non_unique_filesize(self, input_raw_data):
        """
        Removes items
        :param input_raw_data:
        :return:
        """
        file_size_counter = Counter()
        for item in input_raw_data:
            file_size_counter.update([item.file_size])

        self.logger.debug("file_size_counter: {}".format(file_size_counter))

        ret = list()
        for item in input_raw_data:
            if file_size_counter[item.file_size] < 2:
                continue

            ret.append(item)

        return ret

    def _calculate_hashes(self, input_raw_data):
        hash_dict = defaultdict(list)

        for item in input_raw_data:
            hash_value = self._hash_file(item.file_name)

            hash_item = HashedFileData(
                initial_folder_index=item.initial_folder_index,
                file_name=item.file_name,
                file_size=item.file_size,
                base_file_name=os.path.basename(item.file_name),
                hash=hash_value
            )
            hash_dict[hash_value].append(hash_item)

        return hash_dict

    def _remove_files_with_duplicate_hashes(self, hash, input_items):
        self.logger.debug("want remove duplicate files for hash '{}'".format(hash))
        sort_lbd_func = (lambda x: (x.initial_folder_index, len(x.base_file_name), len(x.file_name)))
        sorder_items = sorted(input_items, key=sort_lbd_func, reverse=False)

        items_to_remove = sorder_items[1:]
        for item in items_to_remove:
            self.logger.info("removing file: '{}'".format(item.file_name))
            os.unlink(item.file_name)

        self.logger.debug("will keep item: '{}'".format(sorder_items[0].file_name))

    @staticmethod
    def _hash_file(file_name):
        hasher = hashlib.sha1()
        with open(file_name, "rb") as afile:
            buf = afile.read(DEFAULT_READ_FILE_BLOCKSIZE)
            while len(buf) > 0:
                hasher.update(buf)
                buf = afile.read(DEFAULT_READ_FILE_BLOCKSIZE)

        return hasher.hexdigest()

    def _is_matching_to_valid_extensions(self, filename):
        if not self._acceptable_extensions:
            return True

        for possible_extension in self._acceptable_extensions:
            if fnmatch.fnmatch(filename, possible_extension):
                return True

        return False
