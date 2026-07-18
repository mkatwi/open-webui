import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "backend"
    / "open_webui"
    / "utils"
    / "group_sync.py"
)
spec = importlib.util.spec_from_file_location("group_sync", MODULE_PATH)
assert spec is not None and spec.loader is not None
group_sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(group_sync)

parse_group_names_header = group_sync.parse_group_names_header
sync_user_groups_from_header = group_sync.sync_user_groups_from_header


def test_parse_group_names_header_strips_blanks():
    assert parse_group_names_header(" admins, , editors ,, viewers ") == [
        "admins",
        "editors",
        "viewers",
    ]


def test_sync_user_groups_from_header_syncs_empty_group_list():
    calls = []

    def sync_groups(user_id, group_names):
        calls.append((user_id, group_names))
        return True

    assert sync_user_groups_from_header("user-1", "", sync_groups) is True
    assert calls == [("user-1", [])]


def test_sync_user_groups_from_header_syncs_header_groups():
    calls = []

    def sync_groups(user_id, group_names):
        calls.append((user_id, group_names))
        return True

    assert (
        sync_user_groups_from_header("user-1", "admins, editors", sync_groups) is True
    )
    assert calls == [("user-1", ["admins", "editors"])]
