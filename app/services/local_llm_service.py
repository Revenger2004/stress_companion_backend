import asyncio
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from app.core.config import settings

LOCAL_LLM_MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"
LOCAL_LLM_MAX_NEW_TOKENS = 512

class LocalLLMService:
    def __init__(self):
        self.model_name = LOCAL_LLM_MODEL_NAME
        self.tokenizer = None
        self.model = None
        self._active_chats = {}  # Maps session_id to a list of message dicts
        self._available = False

    def _ensure_model(self):
        """Lazily load the model into memory only when the first request hits."""
        if self._available:
            return True
        try:
            print(f"[LLM-LOCAL] Loading local model: {self.model_name} ...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_name,
                torch_dtype=torch.float32,
            ).to("cpu")
            self.model.eval()
            self._available = True
            print("[LLM-LOCAL] Model loaded successfully on CPU.")
            return True
        except Exception as e:
            print(f"[LLM-LOCAL] Error loading model: {e}")
            self._available = False
            return False

    def _get_or_create_chat(self, session_id: str):
        """Retrieve or initialize the conversation history for a session."""
        if session_id not in self._active_chats:
            # Using the prompt from your script as the default system behavior
            system_instruction = getattr(
                settings, 
                "SYSTEM_INSTRUCTION", 
                "You are a helpful, compassionate mental health interviewer assistant. Follow instructions precisely and be concise."
            )
            self._active_chats[session_id] = [
                {"role": "system", "content": system_instruction}
            ]
        return self._active_chats[session_id]

    def _generate_blocking(self, session_id: str, user_message: str) -> str:
        """The core synchronous text generation logic."""
        if not self._ensure_model():
            raise RuntimeError("Local LLM model not loaded or unavailable.")

        # 1. Fetch history and append the new user message
        history = self._get_or_create_chat(session_id)
        history.append({"role": "user", "content": user_message})

        # 2. Format the history into the Qwen chat template
        text_input = self.tokenizer.apply_chat_template(
            history, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(text_input, return_tensors="pt")

        # 3. Generate the response
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=LOCAL_LLM_MAX_NEW_TOKENS,
                do_sample=True,
                temperature=0.7,
                top_p=0.9,
                repetition_penalty=1.1,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        # 4. Decode only the newly generated tokens
        generated_ids = output[0][inputs["input_ids"].shape[1]:]
        response_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

        # 5. Append the assistant's response to the history for future context
        history.append({"role": "assistant", "content": response_text})

        return response_text

    async def get_chat_response(self, session_id: str, user_message: str) -> str:
        """Async wrapper to prevent blocking the FastAPI event loop."""
        try:
            return await asyncio.to_thread(
                self._generate_blocking,
                session_id,
                user_message,
            )
        except Exception as e:
            # You can map this to your custom exceptions (e.g., LocalLLMServiceError) if you have them
            raise Exception(f"Local LLM error: {str(e)}")

# Instantiate the service
local_llm_service = LocalLLMService()