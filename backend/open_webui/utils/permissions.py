from typing import Any, Callable, Dict


def user_has_permission(
    user: Any,
    permission_key: str,
    default_permissions: Dict[str, Any],
    permission_checker: Callable[[str, str, Dict[str, Any]], bool],
) -> bool:
    if getattr(user, "role", None) == "admin":
        return True

    user_id = getattr(user, "id", None)
    if not user_id:
        return False

    return permission_checker(user_id, permission_key, default_permissions)
