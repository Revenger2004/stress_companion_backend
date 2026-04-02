from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service
from app.services.local_llm_service import local_llm_service
from app.services.chat_db_service import save_chat_messages # Change this import if you put the function in storage_service.py
from app.db.session import get_db

router = APIRouter(prefix="/chat", tags=["Chat"])

# ---------------------------------------------------------------------------
# Original Route: Uses Gemini API
# Endpoint: POST /chat/gemini
# ---------------------------------------------------------------------------
@router.post("/gemini", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: DBSession = Depends(get_db)):
    # 1. Get reply from Gemini
    reply = await gemini_service.get_chat_response(
        session_id=request.session_id,
        user_message=request.message
    )
    
    # 2. Persist to DB using the helper service
    save_chat_messages(
        db=db,
        session_id_str=request.session_id,
        user_message=request.message,
        ai_reply=reply
    )
    
    return ChatResponse(reply=reply)


# ---------------------------------------------------------------------------
# New Route: Uses Local Qwen Model
# Endpoint: POST /chat/local
# ---------------------------------------------------------------------------
@router.post("/local", response_model=ChatResponse)
async def local_chat_endpoint(request: ChatRequest, db: DBSession = Depends(get_db)):
    # 1. Get reply from Local LLM
    reply = await local_llm_service.get_chat_response(
        session_id=request.session_id,
        user_message=request.message
    )
    
    # 2. Persist to DB using the helper service
    save_chat_messages(
        db=db,
        session_id_str=request.session_id,
        user_message=request.message,
        ai_reply=reply
    )
    
    return ChatResponse(reply=reply)