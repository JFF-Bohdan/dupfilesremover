import dataclasses


@dataclasses.dataclass(frozen=True)
class FileInfo:
    file_name: str
    file_size: int
    hast: str = ""


@dataclasses.dataclass
class PerfCounters:
    files_skipped_due_to_unique_size: int = 0
