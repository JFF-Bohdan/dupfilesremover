import dataclasses


@dataclasses.dataclass(frozen=True)
class FileInfo:
    file_name: str
    file_size: int
    creation_timestamp: int | float = 0
    hash: str = ""
    vote: tuple[int, ...] = ()
    folder_prefix: str = ""


@dataclasses.dataclass
class PerfCounters:
    total_files_count: int = 0
    files_skipped_due_to_unique_size: int = 0
    hashed_data_size: int = 0
    unique_files_count: int = 0
