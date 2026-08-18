from fastapi import HTTPException, Request, status

from open_webui.constants import ERROR_MESSAGES
from open_webui.models.users import UserModel
from open_webui.utils.access_control import user_has_permission


def require_permission(request: Request, user: UserModel, permission_key: str) -> None:
    if not user_has_permission(
        user, permission_key, request.app.state.config.USER_PERMISSIONS
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=ERROR_MESSAGES.ACCESS_PROHIBITED,
        )
