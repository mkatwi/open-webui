from typing import Any, Callable, Optional


def user_can_access_file(
    file: Any,
    user: Any,
    access_type: str = "read",
    *,
    get_knowledge_by_id: Optional[Callable[[str], Any]] = None,
    has_access_fn: Optional[Callable[[str, str, Optional[dict]], bool]] = None,
) -> bool:
    if not file or not user:
        return False

    user_id = getattr(user, "id", None)
    if getattr(user, "role", None) == "admin" or getattr(file, "user_id", None) == user_id:
        return True

    file_meta = getattr(file, "meta", None) or {}
    knowledge_base_id = file_meta.get("collection_name")
    if not knowledge_base_id:
        return False

    if get_knowledge_by_id is None:
        from open_webui.models.knowledge import Knowledges

        get_knowledge_by_id = Knowledges.get_knowledge_by_id

    if has_access_fn is None:
        from open_webui.utils.access_control import has_access

        has_access_fn = has_access

    knowledge = get_knowledge_by_id(knowledge_base_id)
    if not knowledge:
        return False

    return (
        getattr(knowledge, "user_id", None) == user_id
        or getattr(user, "role", None) == "admin"
        or has_access_fn(user_id, access_type, getattr(knowledge, "access_control", None))
    )
