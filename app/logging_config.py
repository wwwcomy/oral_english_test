from __future__ import annotations

import logging
import os


def setup_logging() -> logging.Logger:
    """Configure an app logger that works with debugpy + uvicorn reload.

    When uvicorn runs with reload, the serving process imports modules without
    executing the `__main__` block. So we configure at import time.
    """

    logger_obj = logging.getLogger("oral_english_test")
    if logger_obj.handlers:
        return logger_obj

    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    )

    logger_obj.addHandler(handler)
    logger_obj.setLevel(level)
    logger_obj.propagate = False
    return logger_obj
