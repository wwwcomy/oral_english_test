from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from app.logging_config import setup_logging

logger = setup_logging()

APP_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB_PATH = APP_ROOT / "db" / "oral_english_test.sqlite3"
DEFAULT_SCHEMA_PATH = APP_ROOT / "db" / "schema.sql"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def get_db_path() -> Path:
    return Path(os.getenv("DB_PATH", str(DEFAULT_DB_PATH)))


def connect() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row

    # Safety
    conn.execute("PRAGMA foreign_keys = ON")
    # Force single-file rollback journal mode for local/dev usage.
    # This avoids persistent -wal/-shm files.
    conn.execute("PRAGMA journal_mode = DELETE")

    return conn


def init_db(schema_path: Path | None = None) -> None:
    schema_path = schema_path or DEFAULT_SCHEMA_PATH
    if not schema_path.exists():
        raise FileNotFoundError(f"schema.sql not found: {schema_path}")

    sql = schema_path.read_text(encoding="utf-8")
    with connect() as conn:
        conn.executescript(sql)
    logger.info("SQLite initialized: db=%s schema=%s", get_db_path(), schema_path)


@contextmanager
def db_session() -> Iterator[sqlite3.Connection]:
    conn = connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def fetch_all(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    cur = conn.execute(query, params)
    rows = cur.fetchall()
    return [dict(r) for r in rows]


def fetch_one(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    cur = conn.execute(query, params)
    row = cur.fetchone()
    return dict(row) if row else None
