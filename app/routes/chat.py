from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service

# Import the new local service
from app.services.local_llm_service import local_llm_service

router = APIRouter(prefix="/chat", tags=["Chat"])

# ---------------------------------------------------------------------------
# Original Route: Uses Gemini API
# Endpoint: POST /chat/gemini
# ---------------------------------------------------------------------------
@router.post("/gemini", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    reply = await gemini_service.get_chat_response(
        session_id=request.session_id,
        user_message=request.message
    )
    return ChatResponse(reply=reply)


# ---------------------------------------------------------------------------
# New Route: Uses Local Qwen Model
# Endpoint: POST /chat/local
# ---------------------------------------------------------------------------
@router.post("/local", response_model=ChatResponse)
async def local_chat_endpoint(request: ChatRequest):
    reply = await local_llm_service.get_chat_response(
        session_id=request.session_id,
        user_message=request.message
    )
    return ChatResponse(reply=reply)