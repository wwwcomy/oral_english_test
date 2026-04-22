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


def ffmpeg_wav_to_mp3(input_wav: Path, output_mp3: Path) -> Path:
    """Convert a wav file to mp3 via ffmpeg (for browser-friendly playback)."""
    if shutil.which("ffmpeg") is None:
        raise RuntimeError("ffmpeg not found. Install ffmpeg and ensure it is on PATH.")

    output_mp3.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_wav),
        "-codec:a",
        "libmp3lame",
        "-q:a",
        "4",
        str(output_mp3),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"Audio conversion failed (ffmpeg mp3): {msg}")

    if not output_mp3.exists() or output_mp3.stat().st_size == 0:
        raise RuntimeError("ffmpeg produced an empty mp3 output.")

    return output_mp3
