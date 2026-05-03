"""Universal English↔Chinese translator via MyMemory (free, no API key).

Anonymous: ~1000 chars/day. With registered email: ~10000 chars/day.
"""

import httpx
from typing import Optional

_MYMEMORY_URL = "https://api.mymemory.translated.net/get"


def translate_en2zh(text: str, email: Optional[str] = None) -> dict:
    """Translate English to Simplified Chinese via MyMemory."""
    if not text.strip():
        return {"error": "No text provided"}

    params = {"q": text[:500], "langpair": "en|zh-CN"}
    if email:
        params["de"] = email

    try:
        resp = httpx.get(_MYMEMORY_URL, params=params, timeout=10)
        data = resp.json()

        if resp.status_code == 200 and data.get("responseStatus") == 200:
            translated = data["responseData"]["translatedText"]
            match = data["responseData"].get("match", 0)
            return {
                "original": text[:500],
                "translated": translated,
                "quality": round(match * 100, 1),
                "source": "MyMemory",
            }
        return {
            "error": data.get("responseDetails", "Translation failed"),
            "original": text[:500],
        }
    except Exception as e:
        return {"error": str(e), "original": text[:500]}


def translate_zh2en(text: str, email: Optional[str] = None) -> dict:
    """Translate Simplified Chinese to English via MyMemory."""
    if not text.strip():
        return {"error": "No text provided"}

    params = {"q": text[:500], "langpair": "zh-CN|en"}
    if email:
        params["de"] = email

    try:
        resp = httpx.get(_MYMEMORY_URL, params=params, timeout=10)
        data = resp.json()

        if resp.status_code == 200 and data.get("responseStatus") == 200:
            return {
                "original": text[:500],
                "translated": data["responseData"]["translatedText"],
                "quality": round(data["responseData"].get("match", 0) * 100, 1),
                "source": "MyMemory",
            }
        return {"error": data.get("responseDetails", "Translation failed")}
    except Exception as e:
        return {"error": str(e)}
