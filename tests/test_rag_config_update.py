import ast
from pathlib import Path


RETRIEVAL_ROUTER = (
    Path(__file__).resolve().parents[1] / "backend/open_webui/routers/retrieval.py"
)

PRESERVED_FILE_CONFIG_FIELDS = {
    "FILE_MAX_SIZE",
    "FILE_MAX_COUNT",
    "FILE_IMAGE_COMPRESSION_WIDTH",
    "FILE_IMAGE_COMPRESSION_HEIGHT",
}


def _attribute_path(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if isinstance(node, ast.Name):
        parts.append(node.id)
        return tuple(reversed(parts))

    return ()


def test_partial_rag_updates_preserve_file_upload_settings():
    tree = ast.parse(RETRIEVAL_ROUTER.read_text())
    update_function = next(
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "update_rag_config"
    )

    assignments = {}
    for node in ast.walk(update_function):
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            path = _attribute_path(target)
            if (
                len(path) >= 5
                and path[-5:-1] == ("request", "app", "state", "config")
                and path[-1] in PRESERVED_FILE_CONFIG_FIELDS
            ):
                assignments[path[-1]] = node.value

    assert set(assignments) == PRESERVED_FILE_CONFIG_FIELDS

    for field, value in assignments.items():
        assert isinstance(value, ast.IfExp)
        assert _attribute_path(value.body) == ("form_data", field)
        assert _attribute_path(value.orelse) == (
            "request",
            "app",
            "state",
            "config",
            field,
        )
        assert isinstance(value.test, ast.Compare)
        assert _attribute_path(value.test.left) == ("form_data", field)
        assert len(value.test.ops) == 1
        assert isinstance(value.test.ops[0], ast.IsNot)
        assert len(value.test.comparators) == 1
        assert value.test.comparators[0].value is None
