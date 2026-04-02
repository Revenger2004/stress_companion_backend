import uuid
import logging
from sqlalchemy.orm import Session as DBSession
from app.db_models.domain import Message, Session as SessionModel

logger = logging.getLogger(__name__)

def save_chat_messages(db: DBSession, session_id_str: str | None, user_message: str, ai_reply: str):
    """
    Validates the session ID, ensures the session exists, and saves the user and AI messages.
    """
    if not session_id_str or len(session_id_str) < 32:
        return

    # Validate UUID
    try:
        save_sid = uuid.UUID(session_id_str)
    except ValueError:
        logger.warning("Chat history skip: session_id is not a valid UUID")
        return

    # Check if session exists to avoid FK violations
    session_exists = db.query(SessionModel).filter(SessionModel.session_id == save_sid).first()
    
    if session_exists:
        try:
            db.add(Message(session_id=save_sid, role="user", content=user_message))
            db.add(Message(session_id=save_sid, role="assistant", content=ai_reply))
            db.commit()
        except Exception as e:
            logger.error("Failed to save chat history: %s", e)
            db.rollback()
    else:
        logger.warning(
            "Chat history skip: no sessions row for session_id=%s (POST /sessions/ must succeed first)",
            save_sid,
        )