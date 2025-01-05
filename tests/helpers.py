import pathlib

from dupfilesremover import data_types


def convert_file_name_to_file_object(files: list[str]) -> list[data_types.FileInfo]:
    return [data_types.FileInfo(file_name=str(pathlib.Path(item).resolve()), file_size=1) for item in files]


def convert_path_objects_into_file_object(files: list[pathlib.Path]) -> list[data_types.FileInfo]:
    file_info_list = []
    for file in files:
        file_size = file.stat().st_size
        file_info_list.append(
            data_types.FileInfo(
                file_name=str(file.resolve()),
                file_size=file_size,
            )
        )
    return file_info_list
