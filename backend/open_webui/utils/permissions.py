from typing import Any

from fastapi import HTTPException, Request, status

from open_webui.constants import ERROR_MESSAGES
from open_webui.utils.access_control import has_permission


CHAT_FEATURE_PERMISSION_KEYS = {
    "web_search": "features.web_search",
    "image_generation": "features.image_generation",
    "code_interpreter": "features.code_interpreter",
}


def user_has_permission(request: Request, user: Any, permission_key: str) -> bool:
    if getattr(user, "role", None) == "admin":
        return True

    return has_permission(
        user.id,
        permission_key,
        request.app.state.config.USER_PERMISSIONS,
    )


def require_user_permission(request: Request, user: Any, permission_key: str) -> None:
    if not user_has_permission(request, user, permission_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )


def messages_contain_system_role(messages: Any) -> bool:
    if not isinstance(messages, list):
        return False

    return any(
        isinstance(message, dict) and message.get("role") == "system"
        for message in messages
    )


def enforce_chat_system_prompt_permission(
    request: Request, user: Any, messages: Any
) -> None:
    if messages_contain_system_role(messages):
        require_user_permission(request, user, "chat.system_prompt")


def enforce_chat_feature_permissions(
    request: Request, user: Any, features: Any
) -> dict:
    if not isinstance(features, dict):
        return {}

    for feature, permission_key in CHAT_FEATURE_PERMISSION_KEYS.items():
        if features.get(feature):
            require_user_permission(request, user, permission_key)

    return features
