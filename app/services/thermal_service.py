import numpy as np
import cv2
import logging
import onnxruntime as ort
import os
from app.schemas.thermal import ThermalAnalysisResponse

logger = logging.getLogger("thermal_service")
logging.basicConfig(level=logging.INFO)

class ThermalAnalyzer:
    def __init__(self):
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(self.current_dir, "../models/thermal/thermal_model_final.onnx")

        try:
            self.session = ort.InferenceSession(self.model_path)
            self.input_name = self.session.get_inputs()[0].name
            logger.info(f"[THERMAL] Model loaded: {self.model_path}")
        except Exception as e:
            logger.error(f"[THERMAL] CRITICAL FAILURE: {e}")
            raise e

    def _softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    def _preprocess(self, frame):
        try:
            # Resize 224x224 -> Gray -> Norm -> NCHW
            img = cv2.resize(frame, (224, 224))
            if len(img.shape) == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img = img.astype(np.float32) / 255.0
            img = np.expand_dims(img, axis=0) 
            img = np.expand_dims(img, axis=0)
            return img
        except Exception as e:
            logger.error(f"[THERMAL] Preprocessing failed: {e}")
            raise e

    def process_frame(self, image_bytes: bytes) -> ThermalAnalysisResponse:
        try:
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return ThermalAnalysisResponse(status="error", stress_probability=0.0)

            input_tensor = self._preprocess(frame)
            outputs = self.session.run(None, {self.input_name: input_tensor})
            raw_logits = outputs[0][0]

            # Extract Probability (0.0 - 1.0)
            probs = self._softmax(raw_logits)
            stress_prob = float(probs[1]) # Index 1 = Stressed

            logger.info(f"[THERMAL] Prob: {stress_prob:.4f}")

            return ThermalAnalysisResponse(
                status="processed",
                stress_probability=stress_prob,
                metadata={"model": "Thermal_Binary_v1"}
            )

        except Exception as e:
            logger.error(f"[THERMAL] Processing Error: {e}")
            return ThermalAnalysisResponse(status="failed", stress_probability=0.0)

thermal_analyzer = ThermalAnalyzer()