import ast
import importlib.util
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "backend" / "open_webui" / "utils" / "knowledge_files.py"
ROUTER_PATH = ROOT / "backend" / "open_webui" / "routers" / "knowledge.py"


def load_helper_module():
    spec = importlib.util.spec_from_file_location("knowledge_files", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_function_source(function_name):
    source = ROUTER_PATH.read_text()
    tree = ast.parse(source)
    for node in tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            return "\n".join(source.splitlines()[node.lineno - 1 : node.end_lineno])
    raise AssertionError(f"Function not found: {function_name}")


def test_file_access_helper_only_allows_owner_or_admin():
    helper = load_helper_module()
    owner = SimpleNamespace(id="user-1", role="user")
    other = SimpleNamespace(id="user-2", role="user")
    admin = SimpleNamespace(id="admin", role="admin")
    file = SimpleNamespace(user_id="user-1")

    assert helper.user_owns_file_or_is_admin(owner, file)
    assert helper.user_owns_file_or_is_admin(admin, file)
    assert not helper.user_owns_file_or_is_admin(other, file)


def test_file_id_membership_helper_rejects_missing_and_malformed_lists():
    helper = load_helper_module()

    assert helper.file_id_in_knowledge(
        SimpleNamespace(data={"file_ids": ["file-a"]}), "file-a"
    )
    assert not helper.file_id_in_knowledge(
        SimpleNamespace(data={"file_ids": ["file-a"]}), "file-b"
    )
    assert not helper.file_id_in_knowledge(SimpleNamespace(data={}), "file-a")
    assert not helper.file_id_in_knowledge(
        SimpleNamespace(data={"file_ids": "file-a"}), "file-a"
    )


def test_knowledge_remove_does_not_delete_global_file_record():
    remove_source = get_function_source("remove_file_from_knowledge_by_id")

    assert "Files.delete_file_by_id" not in remove_source


def test_knowledge_file_routes_validate_ownership_and_membership_before_processing():
    add_source = get_function_source("add_file_to_knowledge_by_id")
    batch_source = get_function_source("add_files_to_knowledge_batch")
    update_source = get_function_source("update_file_from_knowledge_by_id")
    remove_source = get_function_source("remove_file_from_knowledge_by_id")

    assert "user_owns_file_or_is_admin(user, file)" in add_source
    assert "user_owns_file_or_is_admin(user, file)" in batch_source

    for source in (update_source, remove_source):
        membership_check = source.index(
            "file_id_in_knowledge(knowledge, form_data.file_id)"
        )
        file_lookup = source.index("Files.get_file_by_id(form_data.file_id)")
        vector_delete = source.index("VECTOR_DB_CLIENT.delete")
        assert membership_check < file_lookup
        assert membership_check < vector_delete


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
