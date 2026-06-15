from types import SimpleNamespace

from open_webui.utils import tools as tool_utils


def _user(id="user-1", role="user"):
    return SimpleNamespace(id=id, role=role)


def test_get_tools_skips_private_database_tool_before_loading(monkeypatch):
    private_tool = SimpleNamespace(user_id="owner", access_control={}, specs=[])

    monkeypatch.setattr(tool_utils.Tools, "get_tool_by_id", lambda tool_id: private_tool)
    monkeypatch.setattr(tool_utils, "has_access", lambda *args, **kwargs: False)

    def fail_load(*args, **kwargs):
        raise AssertionError("unauthorized tool module should not be loaded")

    monkeypatch.setattr(tool_utils, "load_tool_module_by_id", fail_load)

    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(TOOLS={})))

    assert (
        tool_utils.get_tools(
            request,
            ["private-tool"],
            _user(),
            {"__user__": {}},
        )
        == {}
    )


def test_get_tools_skips_restricted_tool_server_before_using_credentials(monkeypatch):
    monkeypatch.setattr(tool_utils.Tools, "get_tool_by_id", lambda tool_id: None)
    monkeypatch.setattr(tool_utils, "has_access", lambda *args, **kwargs: False)

    request = SimpleNamespace(
        app=SimpleNamespace(
            state=SimpleNamespace(
                config=SimpleNamespace(
                    TOOL_SERVER_CONNECTIONS=[
                        {
                            "key": "server-secret",
                            "config": {
                                "access_control": {},
                            },
                        }
                    ]
                ),
                TOOL_SERVERS=[
                    {
                        "idx": 0,
                        "url": "https://tool-server.example",
                        "specs": [
                            {
                                "name": "sensitive_tool",
                                "parameters": {"properties": {}},
                            }
                        ],
                    }
                ],
            )
        )
    )

    assert (
        tool_utils.get_tools(
            request,
            ["server:0"],
            _user(),
            {"__user__": {}},
        )
        == {}
    )
