import numpy as np
import cv2
import logging
import onnxruntime as ort
import os
from app.schemas.optical import OpticalAnalysisResponse

logger = logging.getLogger("optical_service")
logging.basicConfig(level=logging.INFO)

class OpticalAnalyzer:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.current_dir, "../models/optical/stress_model.onnx")
        
        try:
            self.session = ort.InferenceSession(self.model_path)
            self.input_name = self.session.get_inputs()[0].name
            self.output_name = self.session.get_outputs()[0].name
            logger.info(f"[OPTICAL] Model loaded: {self.model_path}")
        except Exception as e:
            logger.error(f"[OPTICAL] CRITICAL FAILURE: {e}")
            raise e

    def _preprocess(self, frame):
        try:
            # Resize 48x48 -> Gray -> Norm -> NCHW
            img = cv2.resize(frame, (48, 48))
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = img.astype(np.float32) / 255.0
            img = img.reshape(1, 1, 48, 48)
            return img
        except Exception as e:
            logger.error(f"[OPTICAL] Preprocessing failed: {e}")
            raise e

    def process_frame(self, image_bytes: bytes) -> OpticalAnalysisResponse:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                # Return 0.0 on error so graph doesn't break
                return OpticalAnalysisResponse(status="error", stress_probability=0.0)

            input_tensor = self._preprocess(frame)
            outputs = self.session.run([self.output_name], {self.input_name: input_tensor})
            
            # Extract Probability (0.0 - 1.0)
            raw_output = float(outputs[0][0][0])
            stress_prob = max(0.0, min(1.0, raw_output)) # Clamp safety

            logger.info(f"[OPTICAL] Prob: {stress_prob:.4f}")

            return OpticalAnalysisResponse(
                status="processed",
                stress_probability=stress_prob,
                metadata={"model": "StressNet_v1"}
            )

        except Exception as e:
            logger.error(f"[OPTICAL] Processing Error: {e}")
            return OpticalAnalysisResponse(status="failed", stress_probability=0.0)

optical_analyzer = OpticalAnalyzer()