import dataclasses


@dataclasses.dataclass(frozen=True)
class FileInfo:
    file_name: str
    file_size: int
    creation_timestamp: int | float = 0
    hash: str = ""
    vote: tuple[int | float, ...] = ()
    folder_prefix: str = ""


@dataclasses.dataclass
class PerfCounters:
    total_files_count: int = 0
    files_skipped_due_to_unique_size: int = 0
    files_skipped_by_mask: int = 0
    files_skipped_by_duplicate_name: int = 0
    hashed_data_size: int = 0
    files_skipped_due_to_unique_hash: int = 0
    removed_files_count: int = 0
    reclaimed_space: int = 0
