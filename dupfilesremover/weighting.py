import pathlib

from dupfilesremover import data_types

import first

from loguru import logger


def weight_folders(folders: list[str]) -> dict[str, int]:
    return {path: index for index, path in enumerate(folders)}


def calculate_votes_for_files(
    files: list[data_types.FileInfo],
    weighted_folders: dict[str, int],
) -> list[data_types.FileInfo]:
    result = []

    pathlib_weighted_folders = {pathlib.Path(key): value for key, value in weighted_folders.items()}
    for file in files:
        path_object = pathlib.Path(file.file_name)

        # Looking for a first folder from list of weighted folders where this file belongs
        matched_prefix_info = first.first(
            pathlib_weighted_folders.items(),
            key=lambda weight_data: weight_data[0] in path_object.parents
        )

        if not matched_prefix_info:
            raise RuntimeError(f"Can't find prefix sub-folder for file {file.file_name}")

        logger.debug(f"For file {file.file_name} prefix is {matched_prefix_info}")

        folder_prefix = matched_prefix_info[0]
        # - Main vote - by order of the folder where file belongs (based on order provided in the command line)
        #   For example, let's say we have command line like `folder-1 folder-2 folder-3`
        #   And let's assume that we have same file in both `folder-1` and `folder-2`.
        #   In this case file in `folder-1` will be kept and file in `folder-2` will be removed.
        # Second vote - length of the file name (the shorter the name the higher the chances to keep it)
        # Third vote - is the timestamp of file creation, the older the file the higher changes that it will
        #   NOT be deleted
        votes = (matched_prefix_info[1], len(file.file_name), file.creation_timestamp)
        result.append(
            data_types.FileInfo(
                file_name=file.file_name,
                file_size=file.file_size,
                creation_timestamp=file.creation_timestamp,
                hash=file.hash,
                vote=votes,
                folder_prefix=str(folder_prefix),
            )
        )

    return result


def sort_files_by_votes(files: list[data_types.FileInfo]) -> list[data_types.FileInfo]:
    """
    Sort files by provided votes. This voting can be used to calculate which
    files needs to be deleted and which ones needs to be kept
    """
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
