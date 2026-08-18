from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(relative_path):
    return (ROOT / relative_path).read_text()


def test_stt_supported_content_types_are_normalized_on_save():
    audio_settings = _read("src/lib/components/admin/Settings/Audio.svelte")

    assert ".map((contentType) => contentType.trim())" in audio_settings
    assert ".filter((contentType) => contentType.length > 0)" in audio_settings


def test_stt_backend_uses_normalized_default_content_types():
    audio_router = _read("backend/open_webui/routers/audio.py")
    files_router = _read("backend/open_webui/routers/files.py")

    assert "def normalize_stt_supported_content_types" in audio_router
    assert "def get_stt_supported_content_types" in audio_router
    assert (
        "STT_SUPPORTED_CONTENT_TYPES = normalize_stt_supported_content_types"
        in audio_router
    )
    assert "supported_content_types = get_stt_supported_content_types" in audio_router
    assert "stt_supported_content_types = get_stt_supported_content_types" in files_router
