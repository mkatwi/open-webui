from open_webui.routers.audio import (
    DEFAULT_STT_SUPPORTED_CONTENT_TYPES,
    get_stt_supported_content_types,
    is_stt_supported_content_type,
)


def test_blank_stt_supported_content_types_use_defaults():
    assert get_stt_supported_content_types([""]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES
    assert get_stt_supported_content_types(["  "]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES
    assert get_stt_supported_content_types([]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES
    assert get_stt_supported_content_types(None) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES


def test_stt_supported_content_type_matching_uses_normalized_defaults():
    assert is_stt_supported_content_type("audio/wav", [""])
    assert is_stt_supported_content_type("video/webm", [""])
    assert not is_stt_supported_content_type("video/mp4", [""])


def test_stt_supported_content_type_matching_honors_custom_types():
    assert is_stt_supported_content_type("video/mp4", [" audio/* ", "video/mp4"])
    assert not is_stt_supported_content_type("video/webm", ["audio/*", "video/mp4"])
