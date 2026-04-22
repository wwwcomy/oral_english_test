from __future__ import annotations

import os

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.logging_config import setup_logging
from app.services.asr_service import transcribe_with_faster_whisper
from app.services.llm_service import chat_with_ollama
from app.services.tts_service import synthesize_with_piper
from app.settings import AUDIO_DIR
from app.utils.ffmpeg import ffmpeg_normalize_to_wav_16k_mono, ffmpeg_wav_to_mp3
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

    # TTS: synthesize transcript into mp3 and return a static URL.
    # LLM: transcript/text -> assistant response (Ollama)
    # TTS: synthesize assistant response into mp3.
    user_text = transcript.strip() or text_value
    if not user_text:
        raise HTTPException(status_code=400, detail="No transcript/text available.")

    llm_enabled_env = os.getenv("LLM_ENABLED", "1").lower().strip()
    llm_enabled = llm_enabled_env not in {"0", "false", "no", "n"}

    response_text = user_text
    if llm_enabled:
        try:
            response_text = chat_with_ollama(user_text)
        except RuntimeError as e:
            logger.exception("LLM failed")
            raise HTTPException(status_code=502, detail=str(e))

    tts_text = response_text.strip()
    if not tts_text:
        raise HTTPException(status_code=400, detail="No text available for TTS.")

    try:
        wav_out = AUDIO_DIR / f"tts_{uuid4_hex()}.wav"
        synthesize_with_piper(tts_text, wav_out)

        mp3_name = f"tts_{uuid4_hex()}.mp3"
        mp3_out = AUDIO_DIR / mp3_name
        ffmpeg_wav_to_mp3(wav_out, mp3_out)

        audio_url = f"/static/audio/{mp3_name}"
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("TTS failed")
        raise HTTPException(status_code=500, detail=f"TTS failed: {e}")

    return {
        "transcript": transcript,
        "response": response_text,
        "audio_url": audio_url,
    }


def uuid4_hex() -> str:
    import uuid

    return uuid.uuid4().hex
