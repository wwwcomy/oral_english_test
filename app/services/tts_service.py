from __future__ import annotations

import os
import shutil
import subprocess
import wave
from pathlib import Path
from piper import PiperVoice


voice = PiperVoice.load(
    "/Users/xingnliu/tools/piper-model/amy/en_US-amy-low.onnx")


def synthesize_with_piper(text: str, wav_out: Path) -> Path:
    """Synthesize speech with Piper (Python API) into a wav file.
    """
    wav_out.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(wav_out), "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)

    if not wav_out.exists() or wav_out.stat().st_size == 0:
        raise RuntimeError("Piper produced an empty wav output.")
    return wav_out


def synthesize_with_piper_legacy(text: str, wav_out: Path) -> Path:
    """Synthesize speech with Piper (CLI) into a wav file.

    Requirements:
    - Piper installed and available as `piper` on PATH (or set PIPER_BIN).
    - A voice model path provided via PIPER_MODEL_PATH.

    Env:
    - PIPER_BIN (default: piper)
    - PIPER_MODEL_PATH (required)
    """

    piper_bin = os.getenv("PIPER_BIN", "piper")
    model_path = os.getenv("PIPER_MODEL_PATH", "").strip()
    if not model_path:
        raise RuntimeError(
            "Missing PIPER_MODEL_PATH. Set it to a Piper voice model (.onnx) path."
        )

    if shutil.which(piper_bin) is None:
        raise RuntimeError(
            f"Piper executable not found: {piper_bin}. Install piper or set PIPER_BIN to its full path."
        )

    wav_out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        piper_bin,
        "--model",
        model_path,
        "--output_file",
        str(wav_out),
    ]

    proc = subprocess.run(
        cmd,
        input=text,
        text=True,
        capture_output=True,
    )

    if proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"Piper TTS failed: {msg}")

    if not wav_out.exists() or wav_out.stat().st_size == 0:
        raise RuntimeError("Piper produced an empty wav output.")

    return wav_out
