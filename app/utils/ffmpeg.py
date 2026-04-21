from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path


def ffmpeg_normalize_to_wav_16k_mono(input_path: Path, output_dir: Path) -> Path:
    """Convert input audio to 16kHz mono WAV PCM s16le via ffmpeg."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found. Install ffmpeg and ensure it is on PATH.")

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"normalized_{uuid.uuid4().hex}.wav"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        "-c:a",
        "pcm_s16le",
        str(out_path),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"Audio conversion failed (ffmpeg): {msg}")

    return out_path
