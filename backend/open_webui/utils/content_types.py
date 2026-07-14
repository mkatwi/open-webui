from typing import Optional


DEFAULT_STT_SUPPORTED_CONTENT_TYPES = ["audio/*", "video/webm"]


def get_stt_supported_content_types(configured_content_types: Optional[list[str]]):
    content_types = [
        content_type.strip()
        for content_type in configured_content_types or []
        if isinstance(content_type, str) and content_type.strip()
    ]

    return content_types or DEFAULT_STT_SUPPORTED_CONTENT_TYPES
