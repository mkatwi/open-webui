from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T")


def preserve_existing_if_none(value: T | None, existing: T) -> T:
    return existing if value is None else value


def normalize_stt_supported_content_types(
    content_types: Iterable[str] | None,
) -> list[str]:
    if not content_types:
        return []

    return [
        content_type.strip()
        for content_type in content_types
        if content_type and content_type.strip()
    ]
