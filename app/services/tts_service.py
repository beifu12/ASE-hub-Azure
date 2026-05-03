"""TTS service — generate MP3 pronunciation using Microsoft Edge TTS (free)."""

import hashlib
import asyncio
import shutil
from pathlib import Path

_AUDIO_DIR = Path("/tmp/ase-tts-cache")
_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Also serve from static so Nginx/Cloudflare can cache
_STATIC_DIR = Path(__file__).parent.parent / "static" / "audio"
_STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Check if edge-tts is available
_EDGE_TTS_OK = shutil.which("edge-tts") is not None


async def generate_audio(text: str, voice: str = "en-US-JennyNeural") -> dict:
    """
    Generate MP3 audio for given English text.
    Returns {"path": str, "url": str} or {"error": str}.
    Caches results by text+voice hash.
    """
    if not text or not text.strip():
        return {"error": "No text provided"}

    text = text.strip()
    cache_key = hashlib.md5(f"{text}|{voice}".encode()).hexdigest()
    cache_path = _STATIC_DIR / f"{cache_key}.mp3"

    # Return cached
    if cache_path.exists() and cache_path.stat().st_size > 0:
        return {"path": str(cache_path), "url": f"/static/audio/{cache_key}.mp3", "cached": True}

    if not _EDGE_TTS_OK:
        return {"error": "edge-tts not installed. Run: pip install edge-tts"}

    # Generate with edge-tts
    tmp_path = _AUDIO_DIR / f"{cache_key}.mp3"
    try:
        proc = await asyncio.create_subprocess_exec(
            "edge-tts",
            "--text", text,
            "--voice", voice,
            "--write-media", str(tmp_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            err = stderr.decode()[:200] if stderr else "Unknown error"
            return {"error": f"TTS generation failed: {err}"}

        if not tmp_path.exists() or tmp_path.stat().st_size == 0:
            return {"error": "TTS generated empty file"}

        # Move to static dir for serving
        shutil.move(str(tmp_path), str(cache_path))
        return {"path": str(cache_path), "url": f"/static/audio/{cache_key}.mp3", "cached": False}

    except Exception as e:
        return {"error": f"TTS error: {str(e)}"}


def get_tts_voices() -> list[dict]:
    """Return available voices (hardcoded subset)."""
    return [
        {"id": "en-US-JennyNeural", "name": "Jenny (US Female)", "lang": "en-US"},
        {"id": "en-US-GuyNeural", "name": "Guy (US Male)", "lang": "en-US"},
        {"id": "en-GB-SoniaNeural", "name": "Sonia (UK Female)", "lang": "en-GB"},
        {"id": "en-GB-RyanNeural", "name": "Ryan (UK Male)", "lang": "en-GB"},
        {"id": "zh-CN-XiaoxiaoNeural", "name": "晓晓 (CN Female)", "lang": "zh-CN"},
        {"id": "zh-CN-YunxiNeural", "name": "云希 (CN Male)", "lang": "zh-CN"},
    ]
