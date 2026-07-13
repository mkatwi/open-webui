import importlib
import sys
import types
from types import SimpleNamespace


def test_stt_supported_content_types_uses_defaults_for_blank_entries():
    from open_webui.utils.audio import (
        DEFAULT_STT_SUPPORTED_CONTENT_TYPES,
        get_stt_supported_content_types,
    )

    assert get_stt_supported_content_types(["", "  "]) == (
        DEFAULT_STT_SUPPORTED_CONTENT_TYPES
    )


def test_stt_supported_content_types_trims_and_filters_entries():
    from open_webui.utils.audio import get_stt_supported_content_types

    assert get_stt_supported_content_types([" audio/wav ", "", "video/webm"]) == [
        "audio/wav",
        "video/webm",
    ]


def test_has_permission_treats_null_group_permissions_as_empty(monkeypatch):
    groups = SimpleNamespace(
        get_groups_by_member_id=lambda user_id: [SimpleNamespace(permissions=None)]
    )
    monkeypatch.setitem(
        sys.modules,
        "open_webui.models.groups",
        types.SimpleNamespace(Groups=groups),
    )
    monkeypatch.setitem(
        sys.modules,
        "open_webui.models.users",
        types.SimpleNamespace(Users=object(), UserModel=object),
    )
    monkeypatch.setitem(
        sys.modules,
        "open_webui.config",
        types.SimpleNamespace(
            DEFAULT_USER_PERMISSIONS={"chat": {"file_upload": False}}
        ),
    )
    sys.modules.pop("open_webui.utils.access_control", None)

    access_control = importlib.import_module("open_webui.utils.access_control")

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

    document = _document_from_response({"page_content": None, "metadata": None})

    assert document.page_content == ""
    assert document.metadata == {}
