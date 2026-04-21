import os
import sys
from services.asr_service import transcribe_with_faster_whisper
try:
    import truststore  # type: ignore

    truststore.inject_into_ssl()
except Exception:
    pass
if __name__ == "__main__":
    wav_path = "./static/audio/normalized_697aa17a9a034d00b9703d8affa75021.wav"

    transcript = transcribe_with_faster_whisper(wav_path)
    print(transcript)
