def parse_group_names_header(header_value: str | None) -> list[str]:
    return [name.strip() for name in (header_value or "").split(",") if name.strip()]


def sync_user_groups_from_header(user_id: str, header_value: str | None, sync_groups):
    group_names = parse_group_names_header(header_value)
    return sync_groups(user_id, group_names)
