from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_load_url_query_param_requires_confirmation():
    chat = (ROOT / "src/lib/components/chat/Chat.svelte").read_text()

    load_url_block = chat[
        chat.index("if ($page.url.searchParams.get('load-url'))") : chat.index(
            "if ($page.url.searchParams.get('web-search') === 'true')"
        )
    ]

    assert "window.confirm" in load_url_block
    assert "await uploadWeb(url)" in load_url_block
