from dupfilesremover import consts, file_system


def test_supports_empty_filter():
    files = ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg"]
    result = list(file_system.filter_files_by_masks(files, None))
    assert result == files


def test_filter_by_mask():
    files = ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg", "text-file.txt"]
    expected_result = ["some-image.jpeg", "some-image.jpg", "text-file.txt"]
    result = list(file_system.filter_files_by_masks(files, ["*.jpg", "*.jpeg", "*.txt"]))
    assert result == expected_result


def test_can_filter_for_images():
    files = ["foo.bar", "bizz.bazz", "some-image.jpeg", "some-image.jpg", "text-file.txt"]
    expected_result = ["some-image.jpeg", "some-image.jpg"]
    result = list(file_system.filter_files_by_masks(files, consts.IMAGES))
    assert result == expected_result


