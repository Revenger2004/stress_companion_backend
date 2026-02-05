from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    reply = await gemini_service.get_chat_response(
        session_id=request.session_id,
        user_message=request.message
    )
    return ChatResponse(reply=reply)
