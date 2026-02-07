import numpy as np
import cv2
import logging
import onnxruntime as ort
import os
# Assuming this import exists in your project structure
from app.schemas.optical import OpticalAnalysisResponse

# Configure Logging
logger = logging.getLogger("optical_service")
logging.basicConfig(level=logging.INFO)

class OpticalAnalyzer:
    def __init__(self):
        # 1. Load the ONNX Model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Ensure this path points to your actual .onnx file
        model_path = os.path.join(current_dir, "../models/optical/stress_model.onnx")
        
        try:
            self.session = ort.InferenceSession(model_path)
            # Get input/output names dynamically to avoid hardcoding mismatches
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            logger.info(f"Stress Model Loaded Successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e

    def preprocess(self, frame):
        """
        Prepares the image for the ONNX model.
        Model Expectations:
        - Input Name: 'input_image'
        - Shape: (Batch, Channel, Height, Width) -> (1, 1, 48, 48) [NCHW]
        - Range: 0.0 to 1.0
        """
        try:
            # 1. Resize to model input size (48x48)
            img = cv2.resize(frame, (48, 48))
            
            # 2. Convert to Grayscale if strictly needed (3 channels -> 1 channel)
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 3. Normalize (0-1 range) & Convert to float32
            img = img.astype(np.float32) / 255.0
            
            # 4. Reshape to NCHW (Batch, Channels, Height, Width)
            # PyTorch models require the Channel dimension BEFORE Height/Width
            img = img.reshape(1, 1, 48, 48)
            
            return img
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            raise e

    def process_frame(self, image_bytes: bytes) -> OpticalAnalysisResponse:
        try:
            # 1. Decode Image from bytes
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                logger.warning("Failed to decode image bytes.")
                return OpticalAnalysisResponse(status="error", stress_score=0, is_face_detected=False)

            # 2. Preprocess (Resize -> Gray -> Normalize -> Reshape NCHW)
            input_tensor = self.preprocess(frame)

            # 3. Run Inference
            # session.run returns a list of outputs; we need the first one.
            outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
            
            # 4. Extract Probability
            # Output shape is (1, 1) -> [[0.85]], so we access [0][0]
            # We use .item() or float() to get a native Python float
            stress_probability = float(outputs[0][0][0])

            # 5. Calculate Stress Score (0 - 100)
            final_stress_score = int(stress_probability * 100)

            # Optional: Log the result for debugging
            logger.info(f"Processed Frame. Prob: {stress_probability:.4f}, Score: {final_stress_score}")

            return OpticalAnalysisResponse(
                status="processed",
                stress_score=final_stress_score,
                is_face_detected=True, 
                metadata={
                    "model": "StressNet_ONNX",
                    "probability": stress_probability,
                    "input_shape": str(input_tensor.shape)
                }
            )

        except Exception as e:
            logger.error(f"Inference Error in process_frame: {e}")
            # Return a safe fallback so the API doesn't crash
            return OpticalAnalysisResponse(status="failed", stress_score=0, is_face_detected=False)

# Singleton Instance
optical_analyzer = OpticalAnalyzer()