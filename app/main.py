from __future__ import annotations

import os
import logging
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.logging_config import setup_logging
from app.routers.chat import router as chat_router
from app.settings import STATIC_DIR


logger = setup_logging()

app = FastAPI(title="oral_english_test")

# Serve frontend and generated audio
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(str(STATIC_DIR / "index.html"))


app.include_router(chat_router)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
