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


def _update_rag_config_function():
    tree = ast.parse(RETRIEVAL_ROUTER.read_text())
    return next(
        node
        for node in tree.body
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "update_rag_config"
    )


def _attribute_path(node):
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value

    if isinstance(node, ast.Name):
        parts.append(node.id)
        return tuple(reversed(parts))

    return ()


def _config_assignments_for(fields):
    assignments = {}
    for node in ast.walk(_update_rag_config_function()):
        if not isinstance(node, ast.Assign):
            continue

        for target in node.targets:
            path = _attribute_path(target)
            if (
                len(path) >= 5
                and path[-5:-1] == ("request", "app", "state", "config")
                and path[-1] in fields
            ):
                assignments[path[-1]] = node.value

    return assignments


def _assert_preserved_assignment(field, value):
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


def test_partial_rag_updates_preserve_file_upload_settings():
    assignments = _config_assignments_for(PRESERVED_FILE_CONFIG_FIELDS)

    assert set(assignments) == PRESERVED_FILE_CONFIG_FIELDS

    for field, value in assignments.items():
        _assert_preserved_assignment(field, value)


def test_partial_rag_updates_preserve_reranking_model():
    assignments = _config_assignments_for({"RAG_RERANKING_MODEL"})

    assert set(assignments) == {"RAG_RERANKING_MODEL"}
    _assert_preserved_assignment("RAG_RERANKING_MODEL", assignments["RAG_RERANKING_MODEL"])
