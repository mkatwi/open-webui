from open_webui.routers.audio import (
    DEFAULT_STT_SUPPORTED_CONTENT_TYPES,
    get_stt_supported_content_types,
    sanitize_stt_supported_content_types,
)


def test_sanitize_stt_supported_content_types_removes_blank_values():
    assert sanitize_stt_supported_content_types(
        [" audio/wav ", "", "  ", "video/webm"]
    ) == ["audio/wav", "video/webm"]


def test_get_stt_supported_content_types_falls_back_for_blank_config():
    assert get_stt_supported_content_types(["", "  "]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES


def test_get_stt_supported_content_types_returns_copy_of_defaults():
    content_types = get_stt_supported_content_types([])
    content_types.append("application/octet-stream")

    assert get_stt_supported_content_types([]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES
