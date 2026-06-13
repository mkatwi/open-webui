from open_webui.config import DEFAULT_USER_PERMISSIONS
from open_webui.utils.access_control import fill_missing_permissions


def test_missing_system_prompt_permission_inherits_controls_permission():
    permissions = {"chat": {"controls": False}}

    filled_permissions = fill_missing_permissions(permissions, DEFAULT_USER_PERMISSIONS)

    assert filled_permissions["chat"]["controls"] is False
    assert filled_permissions["chat"]["system_prompt"] is False


def test_explicit_system_prompt_permission_is_preserved():
    permissions = {"chat": {"controls": False, "system_prompt": True}}

    filled_permissions = fill_missing_permissions(permissions, DEFAULT_USER_PERMISSIONS)

    assert filled_permissions["chat"]["controls"] is False
    assert filled_permissions["chat"]["system_prompt"] is True
