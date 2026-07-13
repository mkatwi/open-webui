from typing import Optional


DEFAULT_STT_SUPPORTED_CONTENT_TYPES = ["audio/*", "video/webm"]


def get_stt_supported_content_types(content_types: Optional[list[str]]) -> list[str]:
    supported_content_types = [
        content_type.strip()
        for content_type in (content_types or [])
        if content_type and content_type.strip()
    ]
    return supported_content_types or DEFAULT_STT_SUPPORTED_CONTENT_TYPES
