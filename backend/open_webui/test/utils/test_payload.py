from open_webui.utils.payload import (
    remove_system_prompts_from_body,
    remove_system_prompts_from_settings,
)


def test_remove_system_prompts_from_body_strips_user_controlled_system_fields():
    body = {
        "model": "test-model",
        "messages": [
            {"role": "system", "content": "do not forward"},
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "hi"},
        ],
        "system": "native ollama system",
        "params": {
            "system": "chat control system",
            "temperature": 0.5,
        },
        "options": {
            "system": "ollama option system",
            "num_ctx": 4096,
        },
    }

    sanitized = remove_system_prompts_from_body(body)

    assert sanitized["messages"] == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "hi"},
    ]
    assert "system" not in sanitized
    assert sanitized["params"] == {"temperature": 0.5}
    assert sanitized["options"] == {"num_ctx": 4096}


def test_remove_system_prompts_from_settings_strips_persisted_system_fields():
    settings = {
        "system": "saved global prompt",
        "params": {
            "system": "saved control prompt",
            "stream_response": True,
        },
        "ui": {"theme": "dark"},
    }

    sanitized = remove_system_prompts_from_settings(settings)

    assert sanitized == {
        "params": {"stream_response": True},
        "ui": {"theme": "dark"},
    }
