def remove_user_system_messages_from_body(form_data: dict) -> dict:
    messages = form_data.get("messages")
    if isinstance(messages, list):
        form_data["messages"] = [
            message
            for message in messages
            if not (
                isinstance(message, dict)
                and str(message.get("role", "")).lower() == "system"
            )
        ]

    return form_data
