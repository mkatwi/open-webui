import importlib.util
import sys
import types
from pathlib import Path


class StubHTTPException(Exception):
    def __init__(self, status_code, detail):
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


class StubRequest:
    def __init__(self):
        config = types.SimpleNamespace(USER_PERMISSIONS={})
        self.app = types.SimpleNamespace(state=types.SimpleNamespace(config=config))


def load_permissions_module(permission_allowed=False):
    old_modules = {
        name: sys.modules.get(name)
        for name in [
            "fastapi",
            "open_webui",
            "open_webui.constants",
            "open_webui.utils",
            "open_webui.utils.access_control",
        ]
    }

    fastapi = types.ModuleType("fastapi")
    fastapi.HTTPException = StubHTTPException
    fastapi.Request = object
    fastapi.status = types.SimpleNamespace(HTTP_403_FORBIDDEN=403)

    constants = types.ModuleType("open_webui.constants")
    constants.ERROR_MESSAGES = types.SimpleNamespace(
        ACCESS_PROHIBITED="access prohibited"
    )

    access_control = types.ModuleType("open_webui.utils.access_control")
    access_control.has_permission = lambda user_id, key, permissions: permission_allowed

    open_webui = types.ModuleType("open_webui")
    utils = types.ModuleType("open_webui.utils")

    sys.modules.update(
        {
            "fastapi": fastapi,
            "open_webui": open_webui,
            "open_webui.constants": constants,
            "open_webui.utils": utils,
            "open_webui.utils.access_control": access_control,
        }
    )

    module_path = (
        Path(__file__).resolve().parents[1]
        / "backend"
        / "open_webui"
        / "utils"
        / "permissions.py"
    )
    spec = importlib.util.spec_from_file_location("permission_regression_module", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for name, module_value in old_modules.items():
        if module_value is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = module_value

    return module


def test_system_prompt_permission_denies_user_supplied_system_messages():
    permissions = load_permissions_module(permission_allowed=False)

    assert permissions.messages_contain_system_role(
        [{"role": "system", "content": "override"}]
    )

    try:
        permissions.enforce_chat_system_prompt_permission(
            StubRequest(),
            types.SimpleNamespace(id="user-1", role="user"),
            [{"role": "system", "content": "override"}],
        )
    except StubHTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("system prompt permission bypass was not rejected")


def test_chat_feature_permission_denies_restricted_execution_features():
    permissions = load_permissions_module(permission_allowed=False)

    try:
        permissions.enforce_chat_feature_permissions(
            StubRequest(),
            types.SimpleNamespace(id="user-1", role="user"),
            {"memory": True, "web_search": True},
        )
    except StubHTTPException as exc:
        assert exc.status_code == 403
    else:
        raise AssertionError("web search permission bypass was not rejected")


def test_admin_bypasses_group_feature_permissions():
    permissions = load_permissions_module(permission_allowed=False)

    assert permissions.enforce_chat_feature_permissions(
        StubRequest(),
        types.SimpleNamespace(id="admin-1", role="admin"),
        {"web_search": True, "image_generation": True, "code_interpreter": True},
    ) == {"web_search": True, "image_generation": True, "code_interpreter": True}
