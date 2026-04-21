from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

APP_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = APP_ROOT / "static"
AUDIO_DIR = STATIC_DIR / "audio"

app = FastAPI(title="oral_english_test")

# Serve frontend and generated audio
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/chat")
async def chat(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
) -> dict:
    """V1 placeholder: accepts audio upload and returns a stub response.

    Next steps will implement:
    - ffmpeg normalize to 16kHz mono wav
    - faster-whisper small.en -> transcript
    - ollama HTTP -> response
    - piper -> wav -> ffmpeg mp3 -> audio_url
    """

    text_value = (text or "").strip()
    if file is None and not text_value:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: both 'file' and 'text' are empty. Provide at least one.",
        )

    # Persist upload (useful for debugging)
    if file is not None:
        upload_ext = (Path(file.filename).suffix if file.filename else "") or ".bin"
        upload_id = uuid.uuid4().hex
        upload_path = AUDIO_DIR / f"upload_{upload_id}{upload_ext}"

        AUDIO_DIR.mkdir(parents=True, exist_ok=True)

        with upload_path.open("wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)

    # Stub payload for now
    return {
        "transcript": "(stub) received audio file" if file is not None else f"(stub) text: {text_value}",
        "response": "(stub) Hello! What did you do today?",
        "audio_url": "",
    }


if __name__ == "__main__":
    import uvicorn
    import sys

    port = int(os.getenv("PORT", "8000"))
    # When running as a script (python app/main.py), sys.path[0] points to the
    # app/ directory, so importing "app.main" may fail. Ensure project root is on sys.path.
    sys.path.insert(0, str(APP_ROOT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
