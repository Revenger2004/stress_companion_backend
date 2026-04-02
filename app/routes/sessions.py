from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session as DBSession

from app.db.session import get_db
from app.db_models.domain import Person
from app.schemas.session import (
    SessionCreateResponse, SessionUpdateRequest,
    FrameCreateRequest, MessageCreateRequest, MessageResponse
)
from app.core.security import get_current_user
from app.services import session_service  # Import the new service

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("/", response_model=SessionCreateResponse, status_code=status.HTTP_201_CREATED)
def create_session(current_user: Person = Depends(get_current_user), db: DBSession = Depends(get_db)):
    return session_service.create_new_session(db, current_user.person_id)


@router.put("/{session_id}")
def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return session_service.update_session_status(db, session_id, current_user.person_id, request.status)


@router.post("/{session_id}/frames")
def save_frame(
    session_id: str,
    request: FrameCreateRequest,
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return session_service.save_frame_and_prediction(db, session_id, current_user.person_id, request)


@router.post("/{session_id}/summary")
def save_session_summary(
    session_id: str,
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return session_service.calculate_session_summary(db, session_id, current_user.person_id)


@router.get("/stats")
def get_session_stats(db: DBSession = Depends(get_db), current_user: Person = Depends(get_current_user)):
    return session_service.get_user_statistics(db, current_user.person_id)


@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def save_message(
    session_id: str,
    request: MessageCreateRequest,
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return session_service.save_chat_message(db, session_id, current_user.person_id, request)


@router.get("/{session_id}/messages", response_model=list[MessageResponse])
def get_messages(
    session_id: str,
    current_user: Person = Depends(get_current_user),
    db: DBSession = Depends(get_db)
):
    return session_service.get_chat_history(db, session_id, current_user.person_id)