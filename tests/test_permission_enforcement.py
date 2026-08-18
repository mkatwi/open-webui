from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path):
    return (ROOT / relative_path).read_text()


def test_feature_handlers_require_server_side_permissions():
    middleware = _read("backend/open_webui/utils/middleware.py")

    assert 'require_permission(request, user, "features.web_search")' in middleware
    assert 'require_permission(request, user, "features.image_generation")' in middleware
    assert 'require_permission(request, user, "features.code_interpreter")' in middleware
    assert 'require_permission(request, user, "features.direct_tool_servers")' in middleware


def test_direct_feature_endpoints_require_permissions():
    assert (
        'require_permission(request, user, "features.web_search")'
        in _read("backend/open_webui/routers/retrieval.py")
    )
    assert (
        'require_permission(request, user, "features.image_generation")'
        in _read("backend/open_webui/routers/images.py")
    )
    assert (
        'require_permission(request, user, "features.code_interpreter")'
        in _read("backend/open_webui/routers/utils.py")
    )


def test_system_prompt_permission_is_enforced_server_side():
    middleware = _read("backend/open_webui/utils/middleware.py")
    users_router = _read("backend/open_webui/routers/users.py")

    assert 'require_permission(request, user, "chat.system_prompt")' in middleware
    assert '"system" in updated_user_settings' in users_router
    assert '"chat.system_prompt"' in users_router
    assert 'updated_user_settings.pop("system", None)' in users_router


def test_null_group_permissions_do_not_crash_permission_checks():
    access_control = _read("backend/open_webui/utils/access_control.py")

    assert "group_permissions = group.permissions or {}" in access_control


def test_authoritative_empty_group_lists_are_synced():
    auths = _read("backend/open_webui/routers/auths.py")

    assert "and ENABLE_LDAP_GROUP_MANAGEMENT\n                    and user_groups" not in auths
    assert "if ENABLE_LDAP_GROUP_CREATION and user_groups:" in auths
    assert "Groups.sync_groups_by_group_names(user.id, user_groups)" in auths
    assert "Groups.sync_groups_by_group_names(user.id, group_names)" in auths
