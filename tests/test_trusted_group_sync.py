import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from open_webui.utils.group_sync import (  # noqa: E402
    parse_group_names_header,
    sync_user_groups_from_header,
)


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
