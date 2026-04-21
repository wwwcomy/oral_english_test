from __future__ import annotations

import os
from pathlib import Path

_WHISPER_MODEL = None


def transcribe_with_faster_whisper(wav_path: Path) -> str:
    """Transcribe a wav file using faster-whisper.

    Controlled via env:
    - WHISPER_MODEL (default: small.en)
    - WHISPER_COMPUTE_TYPE (default: int8)
    """
    global _WHISPER_MODEL

    from faster_whisper import WhisperModel

    model_name = os.getenv("WHISPER_MODEL", "small.en")
    compute_type = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

    if _WHISPER_MODEL is None:
        _WHISPER_MODEL = WhisperModel(model_name, compute_type=compute_type)

    segments, _info = _WHISPER_MODEL.transcribe(
        str(wav_path),
        language="en",
        vad_filter=True,
    )

    text_parts: list[str] = []
    for seg in segments:
        t = (seg.text or "").strip()
        if t:
            text_parts.append(t)

    return " ".join(text_parts).strip()
