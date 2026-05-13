from test.util.abstract_integration_test import AbstractPostgresTest
from test.util.mock_user import mock_webui_user


class TestChatCompletions(AbstractPostgresTest):
    BASE_PATH = "/api/chat"

    def setup_method(self):
        super().setup_method()
        from open_webui.models.chats import ChatForm, Chats

        self.chats = Chats
        self.chats.insert_new_chat(
            "victim",
            ChatForm(
                **{
                    "chat": {
                        "history": {
                            "currentId": "user-message",
                            "messages": {
                                "user-message": {
                                    "id": "user-message",
                                    "role": "user",
                                    "content": "private",
                                }
                            },
                        },
                    }
                }
            ),
        )

    def test_completion_cannot_target_another_users_existing_chat(self):
        chat = self.chats.get_chats_by_user_id("victim")[0]

        with mock_webui_user(id="attacker", role="user"):
            response = self.fast_api_client.post(
                self.create_url("/completions"),
                json={
                    "model": "direct-model",
                    "model_item": {"id": "direct-model", "direct": True},
                    "chat_id": chat.id,
                    "id": "assistant-message",
                },
            )

        assert response.status_code == 401
        assert self.chats.get_chat_by_id(chat.id).chat["history"] == {
            "currentId": "user-message",
            "messages": {
                "user-message": {
                    "id": "user-message",
                    "role": "user",
                    "content": "private",
                }
            },
        }
