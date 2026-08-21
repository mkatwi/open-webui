import importlib.util
from pathlib import Path


def load_config_helpers():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "backend"
        / "open_webui"
        / "utils"
        / "config_helpers.py"
    )
    spec = importlib.util.spec_from_file_location("config_helpers", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_preserve_existing_if_none_keeps_current_value_for_partial_updates():
    helpers = load_config_helpers()

    assert helpers.preserve_existing_if_none(None, 25) == 25
    assert helpers.preserve_existing_if_none(0, 25) == 0
    assert helpers.preserve_existing_if_none(False, True) is False


def test_normalize_stt_supported_content_types_drops_blank_entries():
    helpers = load_config_helpers()

    assert helpers.normalize_stt_supported_content_types(["", " audio/* ", "video/webm", " "]) == [
        "audio/*",
        "video/webm",
    ]


def test_normalize_stt_supported_content_types_allows_default_fallback():
    helpers = load_config_helpers()

    assert helpers.normalize_stt_supported_content_types(["", " "]) == []
    assert helpers.normalize_stt_supported_content_types([]) == []
    assert helpers.normalize_stt_supported_content_types(None) == []
