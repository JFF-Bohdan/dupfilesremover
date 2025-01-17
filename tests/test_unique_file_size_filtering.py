from dupfilesremover import data_types, misc


def test_can_remove_files_with_unique_file_size():
    test_data = [
        data_types.FileInfo(
            file_name="file-1",
            file_size=8,
        ),
        data_types.FileInfo(
            file_name="file-2",
            file_size=8,
        ),
        data_types.FileInfo(
            file_name="unique-size-1",
            file_size=12,
        ),
        data_types.FileInfo(
            file_name="unique-size-2",
            file_size=42,
        ),
        data_types.FileInfo(
            file_name="file-3",
            file_size=8,
        ),
    ]

    perf_counters = data_types.PerfCounters()
    result = misc.remove_files_with_unique_size(test_data, perf_counters)
    result = [item.file_name for item in result]
    expected_result = ["file-2", "file-1", "file-3"]

    assert expected_result == result
    assert perf_counters.files_skipped_due_to_unique_size == 2


def test_can_process_single_unique_file():
    test_data = [
        data_types.FileInfo(
            file_name="unique-size-1",
            file_size=12,
        ),
    ]

    perf_counters = data_types.PerfCounters()
    result = list(misc.remove_files_with_unique_size(test_data, perf_counters))
    assert result == []
    assert perf_counters.files_skipped_due_to_unique_size == 1


def test_can_process_only_unique_files():
    test_data = [
        data_types.FileInfo(
            file_name="unique-size-1",
            file_size=12,
        ),
        data_types.FileInfo(
            file_name="unique-size-2",
            file_size=42,
        ),
        data_types.FileInfo(
            file_name="unique-size-3",
            file_size=50,
        ),
    ]

    perf_counters = data_types.PerfCounters()
    result = list(misc.remove_files_with_unique_size(test_data, perf_counters))
    assert result == []
    assert perf_counters.files_skipped_due_to_unique_size == 3


def test_can_process_only_duplicates():
    test_data = [
        data_types.FileInfo(
            file_name="file-1",
            file_size=8,
        ),
        data_types.FileInfo(
            file_name="file-2",
            file_size=8,
        ),
        data_types.FileInfo(
            file_name="file-3",
            file_size=8,
        ),
    ]

    perf_counters = data_types.PerfCounters()
    result = misc.remove_files_with_unique_size(test_data, perf_counters)
    result = [item.file_name for item in result]
    expected_result = ["file-2", "file-1", "file-3"]

    assert expected_result == result
    assert perf_counters.files_skipped_due_to_unique_size == 0
