from collections.abc import Iterable, Mapping
from typing import Any


def get_user_ids_from_session_ids(
    active_session_ids: Iterable[Any], session_pool: Mapping[str, dict]
) -> list[str]:
    user_ids = set()

    for session_id in active_session_ids:
        try:
            sid = session_id[0]
        except (IndexError, TypeError):
            continue

        session = session_pool.get(sid)
        if not session:
            continue

        user_id = session.get("id")
        if user_id:
            user_ids.add(user_id)

    return list(user_ids)
