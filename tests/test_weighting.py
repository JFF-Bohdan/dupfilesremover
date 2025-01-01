from dupfilesremover import weighting


def test_weight_folders():
    test_data = ["folder-1", "folder-2", "folder-3"]
    expected_result = {
        "folder-1": 0,
        "folder-2": 1,
        "folder-3": 2
    }
    result = weighting.weight_folders(test_data)
    assert result == expected_result
