from __future__ import annotations

import uuid
from typing import Any

from app.db.sqlite import fetch_all, fetch_one, utc_now_iso


def create_session(conn, *, title: str, owner_user_id: str = "", status: str = "active", metadata: str | None = None) -> dict[str, Any]:
    now = utc_now_iso()
    session_id = str(uuid.uuid4())

    conn.execute(
        """
        INSERT INTO sessions (
          id, owner_user_id, summary, title, status,
          last_message_time, last_sequence, message_count,
                    create_time, updated_time, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            session_id,
            owner_user_id or None,
            None,
            title,
            status,
            None,
            0,
            0,
            now,
            now,
            metadata,
        ),
    )

    return get_session(conn, session_id=session_id)


def list_sessions(conn, *, limit: int = 50, offset: int = 0) -> list[dict[str, Any]]:
    return fetch_all(
        conn,
        """
        SELECT *
        FROM sessions
        ORDER BY COALESCE(last_message_time, create_time) DESC
        LIMIT ? OFFSET ?
        """,
        (limit, offset),
    )


def get_session(conn, *, session_id: str) -> dict[str, Any]:
    row = fetch_one(conn, "SELECT * FROM sessions WHERE id = ?", (session_id,))
    if not row:
        raise KeyError("session not found")
    return row


def _next_sequence(conn, *, session_id: str) -> int:
    row = fetch_one(conn, "SELECT last_sequence FROM sessions WHERE id = ?", (session_id,))
    if not row:
        raise KeyError("session not found")
    return int(row.get("last_sequence") or 0) + 1


def add_message(
    conn,
    *,
    session_id: str,
    role: str,
    content_text: str,
    agent_name: str | None = None,
    metadata: str | None = None,
) -> dict[str, Any]:
    now = utc_now_iso()
    msg_id = str(uuid.uuid4())
    seq = _next_sequence(conn, session_id=session_id)

    conn.execute(
        """
        INSERT INTO messages (
                    id, session_id, role, agent_name,
          sequence, content, metadata, create_time, update_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            msg_id,
            session_id,
            role,
            agent_name,
            seq,
            content_text,
            metadata,
            now,
            now,
        ),
    )

    # Update session counters
    conn.execute(
        """
        UPDATE sessions
        SET last_message_time = ?,
            last_sequence = ?,
            message_count = message_count + 1,
            updated_time = ?,
        WHERE id = ?
        """,
        (now, seq, now, session_id),
    )

    row = fetch_one(conn, "SELECT * FROM messages WHERE id = ?", (msg_id,))
    return row or {}


def list_messages(conn, *, session_id: str, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
    # Requirement: order by time
    return fetch_all(
        conn,
        """
        SELECT *
        FROM messages
        WHERE session_id = ?
        ORDER BY create_time ASC
        LIMIT ? OFFSET ?
        """,
        (session_id, limit, offset),
    )
