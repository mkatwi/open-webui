from open_webui.routers.audio import (
    DEFAULT_STT_SUPPORTED_CONTENT_TYPES,
    get_stt_supported_content_types,
    sanitize_stt_supported_content_types,
)


def test_sanitize_stt_supported_content_types_removes_empty_entries():
    assert sanitize_stt_supported_content_types([" audio/wav ", "", "  ", "video/webm"]) == [
        "audio/wav",
        "video/webm",
    ]


def test_get_stt_supported_content_types_falls_back_for_blank_config():
    assert get_stt_supported_content_types(["", " "]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES


def test_get_stt_supported_content_types_preserves_explicit_config():
    assert get_stt_supported_content_types(["audio/mpeg"]) == ["audio/mpeg"]
