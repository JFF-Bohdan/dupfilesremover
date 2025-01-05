import collections

from dupfilesremover import data_types, misc


def test_can_group_files_by_hash():
    input_data = [
        data_types.FileInfo(
            file_name="foo",
            file_size=3,
            hash="abc",
        ),
        data_types.FileInfo(
            file_name="bar",
            file_size=3,
            hash="abc",
        ),
        data_types.FileInfo(
            file_name="bizz",
            file_size=4,
            hash="abcdef",
        ),
        data_types.FileInfo(
            file_name="bazz",
            file_size=4,
            hash="abcdef",
        ),
        data_types.FileInfo(
            file_name="unique",
            file_size=42,
            hash="foobar",
        ),
    ]
    result = misc.group_files_by_hash(input_data)

    expected_result = {
        "abc": [
            data_types.FileInfo(
                file_name="foo",
                file_size=3,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="bar",
                file_size=3,
                hash="abc",
            ),
        ],
        "abcdef": [
            data_types.FileInfo(
                file_name="bizz",
                file_size=4,
                hash="abcdef",
            ),
            data_types.FileInfo(
                file_name="bazz",
                file_size=4,
                hash="abcdef",
            ),
        ],
        "foobar": [
            data_types.FileInfo(
                file_name="unique",
                file_size=42,
                hash="foobar",
            ),
        ],
    }

    assert result == expected_result


def test_can_filter_out_files_with_unique_hash():
    input_data = {
        "abc": [
            data_types.FileInfo(
                file_name="foo",
                file_size=3,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="bar",
                file_size=3,
                hash="abc",
            ),
        ],
        "abcdef": [
            data_types.FileInfo(
                file_name="bizz",
                file_size=4,
                hash="abcdef",
            ),
            data_types.FileInfo(
                file_name="bazz",
                file_size=4,
                hash="abcdef",
            ),
        ],
        "foobar": [
            data_types.FileInfo(
                file_name="unique",
                file_size=42,
                hash="foobar",
            ),
        ],
        "uniq": [
            data_types.FileInfo(
                file_name="unique-2",
                file_size=45,
                hash="uniq",
            ),
        ],
    }

    perf_counters = data_types.PerfCounters()
    result = misc.filter_out_unique_files(collections.defaultdict(list, input_data), perf_counters)
    expected_result = {
        "abc": [
            data_types.FileInfo(
                file_name="foo",
                file_size=3,
                hash="abc",
            ),
            data_types.FileInfo(
                file_name="bar",
                file_size=3,
                hash="abc",
            ),
        ],
        "abcdef": [
            data_types.FileInfo(
                file_name="bizz",
                file_size=4,
                hash="abcdef",
            ),
            data_types.FileInfo(
                file_name="bazz",
                file_size=4,
                hash="abcdef",
            ),
        ],
    }
    assert result == expected_result
    assert perf_counters.files_skipped_due_to_unique_hash == 2
