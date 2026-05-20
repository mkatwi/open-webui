from types import SimpleNamespace

from fastapi.responses import Response


def test_sync_external_user_groups_allows_empty_group_list(monkeypatch):
    from open_webui.routers import auths

    calls = []

    class MockGroups:
        @staticmethod
        def create_groups_by_group_names(user_id, group_names):
            raise AssertionError("empty group sync must not try to create groups")

        @staticmethod
        def sync_groups_by_group_names(user_id, group_names):
            calls.append((user_id, group_names))
            return True

    monkeypatch.setattr(auths, "Groups", MockGroups)

    assert auths.sync_external_user_groups("user-1", [], create_missing=True) is True
    assert calls == [("user-1", [])]


def test_trusted_header_signin_syncs_empty_group_header(monkeypatch):
    import asyncio

    from open_webui.routers import auths
    from open_webui.models.auths import SigninForm

    user = SimpleNamespace(
        id="user-1",
        email="user@example.com",
        name="User",
        role="user",
        profile_image_url="/user.png",
    )
    calls = []

    class MockUsers:
        @staticmethod
        def get_user_by_email(email):
            return user

    class MockAuths:
        @staticmethod
        def authenticate_user_by_email(email):
            return user

    class MockGroups:
        @staticmethod
        def sync_groups_by_group_names(user_id, group_names):
            calls.append((user_id, group_names))
            return True

    monkeypatch.setattr(auths, "WEBUI_AUTH_TRUSTED_EMAIL_HEADER", "x-email")
    monkeypatch.setattr(auths, "WEBUI_AUTH_TRUSTED_GROUPS_HEADER", "x-groups")
    monkeypatch.setattr(auths, "WEBUI_AUTH_TRUSTED_NAME_HEADER", None)
    monkeypatch.setattr(auths, "Users", MockUsers)
    monkeypatch.setattr(auths, "Auths", MockAuths)
    monkeypatch.setattr(auths, "Groups", MockGroups)
    monkeypatch.setattr(auths, "create_token", lambda **kwargs: "token")
    monkeypatch.setattr(auths, "get_permissions", lambda user_id, permissions: {})

    request = SimpleNamespace(
        headers={"x-email": "user@example.com"},
        app=SimpleNamespace(
            state=SimpleNamespace(
                config=SimpleNamespace(JWT_EXPIRES_IN="", USER_PERMISSIONS={})
            )
        ),
    )

    result = asyncio.run(
        auths.signin(
            request,
            Response(),
            SigninForm(email="ignored@example.com", password="ignored"),
        )
    )

    assert result["id"] == "user-1"
    assert calls == [("user-1", [])]
