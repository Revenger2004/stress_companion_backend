import asyncio
from google import genai
from google.genai import types

from app.core.config import settings
from app.core.exceptions import (
    GeminiAuthenticationError,
    GeminiQuotaExceededError,
    GeminiServerError,
    GeminiServiceError,
)

class GeminiService:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
            self.model_name = "models/gemini-2.5-flash"
            self._active_chats = {}
        except Exception as e:
            raise GeminiAuthenticationError(
                f"Failed to initialize Gemini client: {str(e)}"
            )

    def _get_or_create_chat(self, session_id: str):
        if session_id not in self._active_chats:
            self._active_chats[session_id] = self.client.chats.create(
                model=self.model_name,
                config=types.GenerateContentConfig(
                    system_instruction=settings.SYSTEM_INSTRUCTION
                ),
            )
        return self._active_chats[session_id]

    def _send_message_blocking(self, session_id: str, user_message: str) -> str:
        chat = self._get_or_create_chat(session_id)
        response = chat.send_message(user_message)
        return response.text

    async def get_chat_response(self, session_id: str, user_message: str) -> str:
        try:
            return await asyncio.to_thread(
                self._send_message_blocking,
                session_id,
                user_message,
            )

        except Exception as e:
            msg = str(e).lower()

            if "api key" in msg or "401" in msg:
                raise GeminiAuthenticationError("Invalid Gemini API key.")
            if "quota" in msg or "429" in msg:
                raise GeminiQuotaExceededError("Gemini quota exceeded.")
            if "500" in msg or "503" in msg:
                raise GeminiServerError("Gemini service unavailable.")

            raise GeminiServiceError(f"Gemini error: {str(e)}")

gemini_service = GeminiService()
