import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


tool_access = load_module(
    "tool_access", "backend/open_webui/utils/tool_access.py"
)
socket_sessions = load_module(
    "socket_sessions", "backend/open_webui/socket/sessions.py"
)


def test_can_use_tool_allows_admin_owner_and_read_access():
    denied = lambda user_id, permission, access_control: False
    allowed = lambda user_id, permission, access_control: True

    assert tool_access.can_use_tool("user-1", "admin", "owner", {}, denied)
    assert tool_access.can_use_tool("user-1", "user", "user-1", {}, denied)
    assert tool_access.can_use_tool(
        "user-1", "user", "owner", {"read": {"user_ids": ["user-1"]}}, allowed
    )


def test_can_use_tool_denies_unshared_tools():
    denied = lambda user_id, permission, access_control: False

    assert not tool_access.can_use_tool(
        "user-1", "user", "owner", {"read": {"user_ids": ["owner"]}}, denied
    )


def test_get_user_ids_from_session_ids_skips_stale_room_participants():
    session_pool = {
        "sid-1": {"id": "user-1"},
        "sid-2": {"id": "user-2"},
    }

    user_ids = socket_sessions.get_user_ids_from_session_ids(
        [("sid-1", "transport-1"), ("stale-sid", "transport-2"), ("sid-2",)],
        session_pool,
    )

    assert set(user_ids) == {"user-1", "user-2"}


def test_get_user_ids_from_session_ids_ignores_empty_sessions():
    user_ids = socket_sessions.get_user_ids_from_session_ids(
        [("empty",), ("missing-id",), (), None],
        {"empty": None, "missing-id": {}},
    )

    assert user_ids == []
