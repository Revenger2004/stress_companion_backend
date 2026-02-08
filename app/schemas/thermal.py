from pydantic import BaseModel
from typing import Optional, Dict, Any

class ThermalAnalysisResponse(BaseModel):
    """
    Standardized lightweight response for Thermal analysis.
    
    Optimized for bandwidth:
    - Returns only the raw probability of the "Stressed" class (0.0 - 1.0).
    - Frontend calculates the Boolean (prob > 0.5).
    """
    status: str
    
    # The Softmax probability of the "Stressed" class (Index 1)
    stress_probability: float  
    
    # Flexible container for debugging info (e.g., raw logits)
    metadata: Optional[Dict[str, Any]] = None