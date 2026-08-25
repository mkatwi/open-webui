import os
from typing import Any, Optional


BYTES_PER_MB = 1024 * 1024


def get_upload_file_size(file: Any) -> Optional[int]:
    size = getattr(file, "size", None)
    if isinstance(size, int):
        return size

    stream = getattr(file, "file", None)
    if stream is None:
        return None

    try:
        current_position = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(current_position)
        return size
    except (AttributeError, OSError):
        return None


def file_size_exceeds_limit(size: Optional[int], max_size_mb: Optional[int]) -> bool:
    return (
        size is not None
        and max_size_mb is not None
        and size > max_size_mb * BYTES_PER_MB
    )


def file_count_exceeds_limit(files: Any, max_count: Optional[int]) -> bool:
    return isinstance(files, list) and max_count is not None and len(files) > max_count
