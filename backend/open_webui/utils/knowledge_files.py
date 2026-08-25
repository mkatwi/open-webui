from typing import Any


def get_knowledge_file_ids(knowledge: Any) -> list[str]:
    data = getattr(knowledge, "data", None) or {}
    file_ids = data.get("file_ids", [])
    return file_ids if isinstance(file_ids, list) else []


def user_owns_file_or_is_admin(user: Any, file: Any) -> bool:
    return getattr(user, "role", None) == "admin" or getattr(
        file, "user_id", None
    ) == getattr(user, "id", None)


def file_id_in_knowledge(knowledge: Any, file_id: str) -> bool:
    return file_id in get_knowledge_file_ids(knowledge)
