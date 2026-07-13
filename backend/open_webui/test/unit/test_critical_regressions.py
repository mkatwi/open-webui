from types import SimpleNamespace


def test_stt_supported_content_types_uses_defaults_for_blank_entries():
    from open_webui.routers.audio import (
        DEFAULT_STT_SUPPORTED_CONTENT_TYPES,
        get_stt_supported_content_types,
    )

    assert get_stt_supported_content_types(["", "  "]) == (
        DEFAULT_STT_SUPPORTED_CONTENT_TYPES
    )


def test_stt_supported_content_types_trims_and_filters_entries():
    from open_webui.routers.audio import get_stt_supported_content_types

    assert get_stt_supported_content_types([" audio/wav ", "", "video/webm"]) == [
        "audio/wav",
        "video/webm",
    ]


def test_has_permission_treats_null_group_permissions_as_empty(monkeypatch):
    from open_webui.utils import access_control

    monkeypatch.setattr(
        access_control.Groups,
        "get_groups_by_member_id",
        lambda user_id: [SimpleNamespace(permissions=None)],
    )

    assert (
        access_control.has_permission(
            "user-id",
            "chat.file_upload",
            {"chat": {"file_upload": True}},
        )
        is True
    )


def test_external_document_response_normalizes_nullable_fields():
    from open_webui.retrieval.loaders.external_document import _document_from_response

    document = _document_from_response(
        {"page_content": None, "metadata": None}
    )

    assert document.page_content == ""
    assert document.metadata == {}
