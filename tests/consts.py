TEST_FOLDERS = ["folder1", "folder2", "folder3"]

# TEST_ORDERBASIC = 1
# TEST_END_TO_END_MOCKED = 10
# TEST_END_TO_END_ACTIVE = 50


TEST_FILES = [
    (
        "folder1",
        "dot-test.txt",
        "The quick brown fox jumps over the lazy dog.",
        "a80f839cd4f83f6c3dafc87feae470045e4eb0d366397d5c6ce34ba1739f734d",
    ),
    (
        "folder1",
        "dot-test-2.txt",
        "The quick brown fox jumps over the lazy dog.",
        "a80f839cd4f83f6c3dafc87feae470045e4eb0d366397d5c6ce34ba1739f734d",
    ),
    (
        "folder1",
        "test.txt",
        "The quick brown fox jumps over the lazy dog",
        "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04",
    ),
    (
        "folder1",
        "test-2.txt",
        "The quick brown fox jumps over the lazy dog",
        "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04",
    ),

    (
        "folder1/sub-folder",
        "unique_size-1.txt",
        "abc",
        "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532",
    ),
    (
        "folder1/sub-folder",
        "unique_size-2.txt",
        "abcdef",
        "59890c1d183aa279505750422e6384ccb1499c793872d6f31bb3bcaa4bc9f5a5",
    ),

    (
        "folder2",
        "dot-test.txt",
        "The quick brown fox jumps over the lazy dog.",
        "a80f839cd4f83f6c3dafc87feae470045e4eb0d366397d5c6ce34ba1739f734d",
    ),
    (
        "folder2",
        "test.txt",
        "The quick brown fox jumps over the lazy dog",
        "69070dda01975c8c120c3aada1b282394e7f032fa9cf32f4cb2259a0897dfc04",
    ),
]

FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS = [
    "folder1/dot-test.txt",
    "folder1/test.txt",
    "folder1/sub-folder/unique_size-1.txt",
    "folder1/sub-folder/unique_size-2.txt",
]


def generate_files_that_needs_to_be_deleted():
    # files_to_remain = [pathlib.Path(file) for file in FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS]
    all_files = [item[0] + "/" + item[1] for item in TEST_FILES]

    return [file for file in all_files if file not in FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS]


FILES_EXPECTED_TO_BE_DELETED_WITHOUT_MASKS = generate_files_that_needs_to_be_deleted()
assert set(FILES_EXPECTED_TO_REMAIN_WITHOUT_MASKS) & set(FILES_EXPECTED_TO_BE_DELETED_WITHOUT_MASKS) == set()
