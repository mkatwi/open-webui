from types import SimpleNamespace

from open_webui.utils import access_control


def test_has_permission_ignores_groups_with_null_permissions(monkeypatch):
    monkeypatch.setattr(
        access_control.Groups,
        "get_groups_by_member_id",
        lambda user_id: [SimpleNamespace(permissions=None)],
    )

    assert (
        access_control.has_permission(
            "user-id",
            "features.notes",
            {"features": {"notes": True}},
        )
        is True
    )
    assert (
        access_control.has_permission(
            "user-id",
            "workspace.tools",
            {"workspace": {"tools": False}},
        )
        is False
    )
