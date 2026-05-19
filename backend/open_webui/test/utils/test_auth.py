from types import SimpleNamespace

import pytest
from fastapi import BackgroundTasks, HTTPException, Response
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from open_webui.utils import auth


def _request_with_headers(headers: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/config",
        "headers": [
            (key.lower().encode(), value.encode()) for key, value in headers.items()
        ],
        "query_string": b"",
        "server": ("testserver", 80),
        "scheme": "http",
        "client": ("testclient", 50000),
    }
    return Request(scope)


def _credentials() -> HTTPAuthorizationCredentials:
    return HTTPAuthorizationCredentials(scheme="Bearer", credentials="jwt-token")


def test_trusted_email_header_allows_case_insensitive_user_email(monkeypatch):
    monkeypatch.setattr(auth, "WEBUI_AUTH_TRUSTED_EMAIL_HEADER", "X-Forwarded-Email")
    monkeypatch.setattr(auth, "decode_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(
        auth.Users,
        "get_user_by_id",
        lambda user_id: SimpleNamespace(
            id=user_id,
            email="User@Example.com",
            role="user",
        ),
    )

    user = auth.get_current_user(
        _request_with_headers({"X-Forwarded-Email": "user@example.com"}),
        Response(),
        BackgroundTasks(),
        _credentials(),
    )

    assert user.email == "User@Example.com"


def test_trusted_email_header_rejects_different_email(monkeypatch):
    monkeypatch.setattr(auth, "WEBUI_AUTH_TRUSTED_EMAIL_HEADER", "X-Forwarded-Email")
    monkeypatch.setattr(auth, "decode_token", lambda token: {"id": "user-1"})
    monkeypatch.setattr(
        auth.Users,
        "get_user_by_id",
        lambda user_id: SimpleNamespace(
            id=user_id,
            email="other@example.com",
            role="user",
        ),
    )

    with pytest.raises(HTTPException) as exc_info:
        auth.get_current_user(
            _request_with_headers({"X-Forwarded-Email": "user@example.com"}),
            Response(),
            BackgroundTasks(),
            _credentials(),
        )

    assert exc_info.value.status_code == 401
