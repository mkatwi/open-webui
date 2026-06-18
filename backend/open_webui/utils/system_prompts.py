def remove_system_prompts_from_body(form_data: dict) -> dict:
    if not isinstance(form_data, dict):
        return form_data

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

    form_data.pop("system", None)

    params = form_data.get("params")
    if isinstance(params, dict):
        params.pop("system", None)

    options = form_data.get("options")
    if isinstance(options, dict):
        options.pop("system", None)

    return form_data


def remove_system_prompts_from_settings(settings: dict) -> dict:
    if not isinstance(settings, dict):
        return settings

    settings.pop("system", None)

    params = settings.get("params")
    if isinstance(params, dict):
        params.pop("system", None)

    return settings
