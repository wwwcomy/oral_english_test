from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db.repository import create_session, list_messages, list_sessions
from app.db.sqlite import db_session

router = APIRouter(prefix="/sessions")


class CreateSessionRequest(BaseModel):
    title: str = Field("New Session", description="Session title")
    owner_user_id: str = Field("", description="Optional owner user id")


@router.post("")
def create_session_endpoint(req: CreateSessionRequest) -> dict:
    with db_session() as conn:
        s = create_session(conn, title=req.title, owner_user_id=req.owner_user_id)
        return s


@router.get("")
def list_sessions_endpoint(limit: int = 50, offset: int = 0) -> list[dict]:
    with db_session() as conn:
        return list_sessions(conn, limit=limit, offset=offset)


@router.get("/{session_id}/messages")
def list_messages_endpoint(session_id: str, limit: int = 200, offset: int = 0) -> list[dict]:
    with db_session() as conn:
        try:
            return list_messages(conn, session_id=session_id, limit=limit, offset=offset)
        except KeyError:
            raise HTTPException(status_code=404, detail="Session not found")
