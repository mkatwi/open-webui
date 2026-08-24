from collections.abc import Callable
from typing import Optional


def can_use_tool(
    user_id: str,
    user_role: str,
    tool_owner_id: Optional[str],
    access_control: Optional[dict],
    has_access_func: Callable[[str, str, Optional[dict]], bool],
) -> bool:
    if user_role == "admin":
        return True

    if tool_owner_id is not None and tool_owner_id == user_id:
        return True

    return has_access_func(user_id, "read", access_control)
