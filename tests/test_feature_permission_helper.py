import importlib.util
from pathlib import Path
from types import SimpleNamespace


def _load_permissions_module():
    module_path = (
        Path(__file__).resolve().parents[1]
        / "backend"
        / "open_webui"
        / "utils"
        / "permissions.py"
    )
    spec = importlib.util.spec_from_file_location("permissions", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_admin_users_do_not_call_permission_checker():
    permissions = _load_permissions_module()

    def deny(*args):
        raise AssertionError("admin users should bypass delegated permission checks")

    assert permissions.user_has_permission(
        SimpleNamespace(id="admin-user", role="admin"),
        "features.code_interpreter",
        {"features": {"code_interpreter": False}},
        deny,
    )


def test_regular_users_delegate_to_permission_checker():
    permissions = _load_permissions_module()
    calls = []

    def allow(user_id, permission_key, default_permissions):
        calls.append((user_id, permission_key, default_permissions))
        return permission_key == "features.web_search"

    default_permissions = {"features": {"web_search": True}}

    assert permissions.user_has_permission(
        SimpleNamespace(id="regular-user", role="user"),
        "features.web_search",
        default_permissions,
        allow,
    )
    assert calls == [
        ("regular-user", "features.web_search", default_permissions),
    ]


def test_users_without_ids_are_denied():
    permissions = _load_permissions_module()

    assert not permissions.user_has_permission(
        SimpleNamespace(role="user"),
        "features.direct_tool_servers",
        {"features": {"direct_tool_servers": True}},
        lambda *args: True,
    )
