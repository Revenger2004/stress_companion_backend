from pydantic import BaseModel
from typing import Optional

class ThermalAnalysisResponse(BaseModel):
    """
    Standard response format for the Thermal analysis pipeline.
    """
    status: str
    
    # The Softmax probability of Output[1] (Stressed). 
    # Using float for precision since the model outputs raw logits/probs.
    stress_probability: float  
    
    # Derived from comparing Output[0] vs Output[1].
    # True if Output[1] (Stressed) > Output[0] (Non-Stressed).
    is_stressed: bool          
    
    # Optional field to verify if the thermal frame was valid 
    # (e.g. not empty, correct shape) before processing.
    is_frame_valid: bool       

    # We use 'metadata' to store raw logits or intermediate values
    # (e.g. {"raw_logits": [-0.5, 2.3], "non_stress_prob": 0.05})
    metadata: Optional[dict] = None