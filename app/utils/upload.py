from __future__ import annotations

import uuid
from pathlib import Path

from fastapi import UploadFile


async def save_upload_file_to_dir(upload: UploadFile, target_dir: Path) -> Path:
    """Save an uploaded file to disk and return the saved path."""
    target_dir.mkdir(parents=True, exist_ok=True)

    upload_ext = (Path(upload.filename).suffix if upload.filename else "") or ".bin"
    upload_id = uuid.uuid4().hex
    upload_path = target_dir / f"upload_{upload_id}{upload_ext}"

    with upload_path.open("wb") as f:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    return upload_path
