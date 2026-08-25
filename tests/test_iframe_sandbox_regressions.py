from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTED_IFRAME_FILES = [
    ROOT / "src" / "lib" / "components" / "chat" / "Artifacts.svelte",
    (
        ROOT
        / "src"
        / "lib"
        / "components"
        / "chat"
        / "Messages"
        / "Markdown"
        / "HTMLToken.svelte"
    ),
]


def test_script_enabled_chat_iframes_do_not_allow_downloads_by_default():
    for path in SCRIPTED_IFRAME_FILES:
        source = path.read_text()
        assert "allow-downloads" not in source


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
