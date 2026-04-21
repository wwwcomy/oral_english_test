from __future__ import annotations

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.logging_config import setup_logging
from app.services.asr_service import transcribe_with_faster_whisper
from app.settings import AUDIO_DIR
from app.utils.ffmpeg import ffmpeg_normalize_to_wav_16k_mono
from app.utils.upload import save_upload_file_to_dir

logger = setup_logging()
router = APIRouter()


@router.post("/chat")
async def chat(
    file: UploadFile | None = File(None),
    text: str | None = Form(None),
) -> dict:
    logger.info("Received /chat request: file=%s, text=%s", file.filename if file else None, text)

    text_value = (text or "").strip()
    if file is None and not text_value:
        raise HTTPException(
            status_code=400,
            detail="Invalid request: both 'file' and 'text' are empty. Provide at least one.",
        )

    transcript = ""
    if file is not None:
        try:
            upload_path = await save_upload_file_to_dir(file, AUDIO_DIR)
            logger.info("Saved uploaded file to %s", upload_path)

            wav_path = ffmpeg_normalize_to_wav_16k_mono(upload_path, AUDIO_DIR)
            logger.info("Normalized audio to %s", wav_path)

            transcript = transcribe_with_faster_whisper(wav_path)
            logger.info("ASR transcript: %s", transcript)
        except RuntimeError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.exception("ASR failed")
            raise HTTPException(status_code=500, detail=f"ASR failed: {e}")
    else:
        transcript = text_value

    # LLM/TTS still stubbed for now.
    return {
        "transcript": transcript,
        "response": "(stub) Hello! What did you do today?",
        "audio_url": "",
    }
