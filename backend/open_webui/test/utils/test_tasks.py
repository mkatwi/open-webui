import asyncio
from types import SimpleNamespace

from open_webui import tasks


def _request(redis=None):
    return SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(redis=redis)))


def test_get_task_chat_id_ignores_unscoped_local_tasks(monkeypatch):
    monkeypatch.setattr(
        tasks,
        "chat_tasks",
        {
            "chat-1": ["task-1"],
            None: ["task-without-chat"],
            "chat-2": ["task-2"],
        },
    )

    assert asyncio.run(tasks.get_task_chat_id(_request(), "task-1")) == "chat-1"
    assert asyncio.run(tasks.get_task_chat_id(_request(), "task-without-chat")) is None
    assert asyncio.run(tasks.get_task_chat_id(_request(), "missing-task")) is None


def test_get_task_chat_id_reads_redis_mapping():
    class FakeRedis:
        async def hget(self, key, task_id):
            assert key == tasks.REDIS_TASKS_KEY
            assert task_id == "task-redis"
            return "chat-redis"

    assert (
        asyncio.run(tasks.get_task_chat_id(_request(redis=FakeRedis()), "task-redis"))
        == "chat-redis"
    )
