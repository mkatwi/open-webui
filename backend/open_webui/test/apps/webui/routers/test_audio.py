from open_webui.routers.audio import (
    DEFAULT_STT_SUPPORTED_CONTENT_TYPES,
    get_stt_supported_content_types,
    is_stt_content_type_supported,
    normalize_content_type,
    normalize_content_types,
)


def test_stt_content_type_matching_ignores_mime_parameters():
    assert is_stt_content_type_supported("audio/webm; codecs=opus", [])
    assert is_stt_content_type_supported("video/webm; codecs=vp9, opus", [])


def test_stt_content_type_matching_normalizes_case_and_whitespace():
    supported_content_types = [" AUDIO/* ", "", "video/webm; codecs=opus"]

    assert normalize_content_type(" Audio/WAV ; charset=binary") == "audio/wav"
    assert normalize_content_types(supported_content_types) == ["audio/*", "video/webm"]
    assert is_stt_content_type_supported("Audio/WAV; charset=binary", supported_content_types)


def test_stt_content_type_matching_falls_back_to_defaults_for_blank_config():
    assert get_stt_supported_content_types(["", " "]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES
    assert is_stt_content_type_supported("audio/mp4", ["", " "])
    assert not is_stt_content_type_supported("image/png", ["", " "])
