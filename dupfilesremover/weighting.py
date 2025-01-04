import first
# import collections

from loguru import logger

from dupfilesremover import data_types


def weight_folders(folders: list[str]) -> dict[str, int]:
    return {path: index for index, path in enumerate(folders)}
    # result = {}
    # folders_count = len(folders)
    # for index, path in enumerate(folders):
        # result[path] = folders_count - index
        # result[path] = index

    # return result


def calculate_votes_for_files(
    files: list[data_types.FileInfo],
    weighted_folders: dict[str, int],
) -> list[data_types.FileInfo]:
    result = []

    for file in files:
        matched_prefix_info = first.first(
            weighted_folders.items(),
            key=lambda weight_data: file.file_name.startswith(weight_data[0])
        )

        if not matched_prefix_info:
            raise RuntimeError(f"Can't find prefix sub-folder for file {file.file_name}")

        logger.debug(f"For file {file.file_name} prefix is {matched_prefix_info}")

        folder_prefix = matched_prefix_info[0]
        votes = (matched_prefix_info[1], len(file.file_name), file.creation_timestamp)
        result.append(
            data_types.FileInfo(
                file_name=file.file_name,
                file_size=file.file_size,
                creation_timestamp=file.creation_timestamp,
                hash=file.hash,
                vote=votes,
                folder_prefix=folder_prefix,
            )
        )

    return result


def sort_files_by_votes(files: list[data_types.FileInfo]) -> list[data_types.FileInfo]:
    return sorted(files, key=lambda x: x.vote)


def vote_and_sort_duplicates(
    hash_to_files: dict[str, list[data_types.FileInfo]],
    weighted_folders: dict[str, int],
) -> dict[str, list[data_types.FileInfo]]:
    result = {}
    keys = list(hash_to_files.keys())
    for key in keys:
        voted_files = calculate_votes_for_files(
            hash_to_files[key],
            weighted_folders
        )

        sorted_voted_files = sort_files_by_votes(
            voted_files
        )
        result[key] = sorted_voted_files

    return result
