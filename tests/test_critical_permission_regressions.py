import importlib.util
from pathlib import Path


def load_module(module_name: str, relative_path: str):
    module_path = Path(__file__).parents[1] / relative_path
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


content_types = load_module(
    "content_types", "backend/open_webui/utils/content_types.py"
)
messages = load_module("messages", "backend/open_webui/utils/messages.py")

DEFAULT_STT_SUPPORTED_CONTENT_TYPES = content_types.DEFAULT_STT_SUPPORTED_CONTENT_TYPES
get_stt_supported_content_types = content_types.get_stt_supported_content_types
remove_user_system_messages_from_body = messages.remove_user_system_messages_from_body


def test_blank_stt_content_types_fall_back_to_defaults():
    assert get_stt_supported_content_types(["", "  "]) == DEFAULT_STT_SUPPORTED_CONTENT_TYPES


def test_stt_content_types_are_trimmed_and_empty_entries_removed():
    assert get_stt_supported_content_types([" audio/wav ", "", "video/mp4"]) == [
        "audio/wav",
        "video/mp4",
    ]


def test_user_system_messages_are_removed_from_payload():
    payload = {
        "messages": [
            {"role": "system", "content": "user controlled"},
            {"role": "user", "content": "hello"},
            {"role": "SYSTEM", "content": "also user controlled"},
            {"role": "assistant", "content": "hi"},
        ]
    }

    assert remove_user_system_messages_from_body(payload) == {
        "messages": [
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ]
    }
