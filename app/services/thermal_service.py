import numpy as np
import cv2
import logging
import onnxruntime as ort
import os
from app.schemas.thermal import ThermalAnalysisResponse  # Assuming you placed the schema here

# Configure Logging
logger = logging.getLogger("thermal_service")
logging.basicConfig(level=logging.INFO)

class ThermalAnalyzer:
    def __init__(self):
        # 1. Load the ONNX Model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Update this filename to match your actual thermal model file
        model_path = os.path.join(current_dir, "../models/thermal/thermal_model_final.onnx")
        
        try:
            # Initialize ONNX Runtime Session
            self.session = ort.InferenceSession(model_path)
            self.input_name = self.session.get_inputs()[0].name
            logger.info(f"Thermal Model Loaded Successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load thermal model: {e}")
            # Depending on policy, you might want to suppress this or raise
            raise e

    def softmax(self, x):
        """Compute softmax values for raw logits."""
        e_x = np.exp(x - np.max(x)) # Subtract max for numerical stability
        return e_x / e_x.sum()

    def preprocess(self, frame):
        """
        Thermal Model Specs:
        1. Convert to Grayscale
        2. Resize to 224x224
        3. Normalize (0-255 -> 0.0-1.0 float32)
        4. Shape: (Batch, Channels, Height, Width) -> (1, 1, 224, 224)
        """
        # 1. Resize to 224x224
        img = cv2.resize(frame, (224, 224))
        
        # 2. Convert to Grayscale
        # Even if input is thermal, OpenCV decodes as BGR by default, so we convert back to 1 channel
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 3. Normalize to float32 (0.0 - 1.0)
        img = img.astype(np.float32) / 255.0
        
        # 4. Reshape to NCHW (1, 1, 224, 224)
        # Current shape is (224, 224). We need to add Batch and Channel dims.
        img = np.expand_dims(img, axis=0) # Shape becomes (1, 224, 224)
        img = np.expand_dims(img, axis=0) # Shape becomes (1, 1, 224, 224)
        
        return img

    def process_frame(self, image_bytes: bytes) -> ThermalAnalysisResponse:
        try:
            # 1. Decode Image
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return ThermalAnalysisResponse(
                    status="error", 
                    stress_probability=0.0, 
                    is_stressed=False, 
                    is_frame_valid=False
                )

            # 2. Preprocess
            input_tensor = self.preprocess(frame)

            # 3. Run Inference
            outputs = self.session.run(None, {self.input_name: input_tensor})
            raw_logits = outputs[0][0]  # Shape: [2] -> [Non-Stressed, Stressed]

            # 4. Calculate Probabilities (Softmax)
            probabilities = self.softmax(raw_logits)
            
            # Extract specific class probabilities
            prob_non_stressed = float(probabilities[0])
            prob_stressed = float(probabilities[1])

            # 5. Determine Classification
            # If prob_stressed > prob_non_stressed, then is_stressed = True
            is_stressed = prob_stressed > prob_non_stressed

            return ThermalAnalysisResponse(
                status="processed",
                stress_probability=prob_stressed,
                is_stressed=is_stressed,
                is_frame_valid=True,
                metadata={
                    "raw_logits": raw_logits.tolist(),
                    "non_stress_prob": prob_non_stressed,
                    "model_type": "Thermal_Binary_Classifier"
                }
            )

        except Exception as e:
            logger.error(f"Thermal Inference Error: {e}")
            return ThermalAnalysisResponse(
                status="failed", 
                stress_probability=0.0, 
                is_stressed=False, 
                is_frame_valid=False,
                metadata={"error": str(e)}
            )

# Singleton Instance
thermal_analyzer = ThermalAnalyzer()