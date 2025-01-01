def weight_folders(folders: list[str]) -> dict[str, int]:

    result = {}
    folders_count = len(folders)
    for index, path in enumerate(folders):
        result[path] = folders_count - index

    return result
