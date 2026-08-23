import importlib.util
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]


def load_file_access_module():
    module_path = REPO_ROOT / "backend/open_webui/utils/file_access.py"
    spec = importlib.util.spec_from_file_location("file_access", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


file_access = load_file_access_module()


def user(id="user-1", role="user"):
    return SimpleNamespace(id=id, role=role)


def file(id="file-1", user_id="owner-1", meta=None):
    return SimpleNamespace(id=id, user_id=user_id, meta=meta)


def test_owner_and_admin_can_access_file_without_knowledge_lookup():
    def fail_lookup(_):
        raise AssertionError("knowledge lookup should not run")

    owned_file = file(user_id="user-1")

    assert file_access.user_can_access_file(
        owned_file, user("user-1"), "write", get_knowledge_by_id=fail_lookup
    )
    assert file_access.user_can_access_file(
        owned_file, user("admin-1", "admin"), "write", get_knowledge_by_id=fail_lookup
    )


def test_user_without_owner_or_knowledge_access_is_denied():
    assert not file_access.user_can_access_file(
        file(user_id="owner-1"),
        user("user-1"),
        "read",
        get_knowledge_by_id=lambda _: None,
    )


def test_knowledge_access_uses_requested_access_type():
    knowledge = SimpleNamespace(
        id="kb-1",
        user_id="owner-2",
        access_control={
            "read": {"user_ids": ["user-1"], "group_ids": []},
            "write": {"user_ids": [], "group_ids": []},
        },
    )

    def has_access_fn(user_id, access_type, access_control):
        return user_id in access_control.get(access_type, {}).get("user_ids", [])

    shared_file = file(user_id="owner-1", meta={"collection_name": "kb-1"})

    assert file_access.user_can_access_file(
        shared_file,
        user("user-1"),
        "read",
        get_knowledge_by_id=lambda _: knowledge,
        has_access_fn=has_access_fn,
    )
    assert not file_access.user_can_access_file(
        shared_file,
        user("user-1"),
        "write",
        get_knowledge_by_id=lambda _: knowledge,
        has_access_fn=has_access_fn,
    )


def test_retrieval_processing_enforces_server_side_file_access():
    retrieval_source = (REPO_ROOT / "backend/open_webui/routers/retrieval.py").read_text()

    assert (
        'file = _get_file_for_processing(form_data.file_id, "write", user)'
        in retrieval_source
    )
    assert 'file = _get_file_for_processing(file.id, "write", user)' in retrieval_source
    assert 'text_content = (file.data or {}).get("content", "")' in retrieval_source
