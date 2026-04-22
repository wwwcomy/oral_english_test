from __future__ import annotations

import os
from typing import Any

import httpx

from app.logging_config import setup_logging

logger = setup_logging()

_OLLAMA_CLIENT: httpx.Client | None = None


def _get_ollama_client() -> httpx.Client:
    global _OLLAMA_CLIENT
    if _OLLAMA_CLIENT is None:
        timeout = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
        _OLLAMA_CLIENT = httpx.Client(timeout=timeout)
    return _OLLAMA_CLIENT


def chat_with_ollama(user_text: str) -> str:
    """Call Ollama /api/chat and return assistant text.

    Env:
    - OLLAMA_BASE_URL (default http://localhost:11434)
    - OLLAMA_MODEL (default qwen3.5:9b)
    - OLLAMA_TIMEOUT_SECONDS (default 60)
    - OLLAMA_THINK (default false)
    - OLLAMA_SYSTEM_PROMPT (optional)

    Note: For Qwen models, `think: false` can reduce hidden chain-of-thought output.
    """

    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
    model = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")

    system_prompt = os.getenv(
        "OLLAMA_SYSTEM_PROMPT",
        "\n".join(
            [
                "You are a friendly English teacher talking to a 10-year-old child.",
                "Use simple words and short sentences.",
                "Be encouraging.",
                "Always ask one short follow-up question.",
                "Reply in English only.",
            ]
        ),
    )

    think_env = os.getenv("OLLAMA_THINK", "false").lower().strip()
    think = think_env in {"1", "true", "yes", "y"}

    payload: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "think": think,
        "stream": False,
    }

    url = f"{base_url}/api/chat"
    logger.info("Calling Ollama: url=%s model=%s think=%s", url, model, think)

    client = _get_ollama_client()
    try:
        r = client.post(url, json=payload)
    except httpx.HTTPError as e:
        raise RuntimeError(f"Failed to connect to Ollama at {base_url}: {e}")

    if r.status_code != 200:
        raise RuntimeError(f"Ollama error {r.status_code}: {r.text}")

    data = r.json()

    # /api/chat style
    msg = data.get("message")
    if isinstance(msg, dict) and isinstance(msg.get("content"), str):
        return msg.get("content", "").strip()

    # fallback: /api/generate style
    if isinstance(data.get("response"), str):
        return data.get("response", "").strip()

    raise RuntimeError(f"Unexpected Ollama response format: {data}")
