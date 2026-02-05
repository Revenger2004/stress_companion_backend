from pydantic import BaseModel
from typing import Optional

class OpticalAnalysisResponse(BaseModel):
    """
    Standard response format for the Optical (RGB) analysis pipeline.
    """
    status: str
    stress_score: int         # 0-100 scale
    is_face_detected: bool
    # We add 'metadata' for future expansion (e.g. blink rate, emotion label)
    # without breaking the frontend contract.
    metadata: Optional[dict] = None