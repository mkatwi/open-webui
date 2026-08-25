import ast
import importlib.util
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
HELPER_PATH = ROOT / "backend" / "open_webui" / "utils" / "file_limits.py"
FILES_ROUTER_PATH = ROOT / "backend" / "open_webui" / "routers" / "files.py"
MIDDLEWARE_PATH = ROOT / "backend" / "open_webui" / "utils" / "middleware.py"


def load_helper_module():
    spec = importlib.util.spec_from_file_location("file_limits", HELPER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def get_function_source(path, function_name):
    source = path.read_text()
    tree = ast.parse(source)
    for node in tree.body:
        if (
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == function_name
        ):
            return "\n".join(source.splitlines()[node.lineno - 1 : node.end_lineno])
    raise AssertionError(f"Function not found: {function_name}")


def test_upload_file_size_uses_size_attribute_when_present():
    helper = load_helper_module()
    upload = SimpleNamespace(size=123, file=BytesIO(b"ignored"))

    assert helper.get_upload_file_size(upload) == 123


def test_upload_file_size_falls_back_to_stream_without_changing_position():
    helper = load_helper_module()
    stream = BytesIO(b"abcdef")
    stream.seek(2)
    upload = SimpleNamespace(file=stream)

    assert helper.get_upload_file_size(upload) == 6
    assert stream.tell() == 2


def test_file_size_and_count_limits_are_enforced_only_when_configured():
    helper = load_helper_module()

    assert helper.file_size_exceeds_limit(2 * helper.BYTES_PER_MB + 1, 2)
    assert not helper.file_size_exceeds_limit(2 * helper.BYTES_PER_MB, 2)
    assert not helper.file_size_exceeds_limit(100, None)
    assert helper.file_count_exceeds_limit([{}, {}, {}], 2)
    assert not helper.file_count_exceeds_limit([{}, {}], 2)
    assert not helper.file_count_exceeds_limit([{}, {}, {}], None)


def test_upload_route_checks_size_before_storage_write():
    upload_source = get_function_source(FILES_ROUTER_PATH, "upload_file")

    size_check = upload_source.index("file_size_exceeds_limit(file_size, max_file_size)")
    storage_write = upload_source.index("Storage.upload_file")
    assert size_check < storage_write
    assert "HTTP_413_REQUEST_ENTITY_TOO_LARGE" in upload_source


def test_chat_payload_checks_client_file_count_before_model_knowledge_append():
    process_source = get_function_source(MIDDLEWARE_PATH, "process_chat_payload")

    count_check = process_source.index("file_count_exceeds_limit(")
    model_knowledge = process_source.index("model_knowledge =")
    assert count_check < model_knowledge


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
