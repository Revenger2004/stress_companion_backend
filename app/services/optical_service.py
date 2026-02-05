import numpy as np
import cv2
import logging
import onnxruntime as ort
import os
import random
from app.schemas.optical import OpticalAnalysisResponse

# Configure Logging
logger = logging.getLogger("optical_service")
logging.basicConfig(level=logging.INFO)

class OpticalAnalyzer:
    def __init__(self):
        # 1. Load the ONNX Model
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Adjust this path if your models folder is elsewhere relative to services/
        model_path = os.path.join(current_dir, "../models/mobilenetv2-7.onnx")
        
        try:
            self.session = ort.InferenceSession(model_path)
            self.input_name = self.session.get_inputs()[0].name
            logger.info(f"MobileNetV2 Loaded Successfully from {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise e

    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x)) # Subtract max for numerical stability
        return e_x / e_x.sum()

    def preprocess(self, frame):
        """
        MobileNetV2 expects:
        1. Resize to 224x224
        2. RGB Color (not BGR)
        3. Normalization (Mean/Std)
        4. Shape: (Batch, Channels, Height, Width) -> (1, 3, 224, 224)
        """
        # Resize to model input size (224x224)
        img = cv2.resize(frame, (224, 224))
        
        # Convert BGR (OpenCV default) to RGB
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Normalize (Standard ImageNet mean/std)
        img = img.astype(np.float32) / 255.0
        mean = np.array([0.485, 0.456, 0.406])
        std = np.array([0.229, 0.224, 0.225])
        img = (img - mean) / std
        
        # Transpose from HWC (224, 224, 3) to CHW (3, 224, 224)
        img = img.transpose(2, 0, 1)
        
        # Add Batch Dimension: (1, 3, 224, 224)
        img = np.expand_dims(img, axis=0)
        return img.astype(np.float32)

    def process_frame(self, image_bytes: bytes) -> OpticalAnalysisResponse:
        try:
            # 1. Decode Image
            nparr = np.frombuffer(image_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                return OpticalAnalysisResponse(status="error", stress_score=0, is_face_detected=False)

            # 2. Preprocess
            input_tensor = self.preprocess(frame)

            # 3. Run Inference
            outputs = self.session.run(None, {self.input_name: input_tensor})
            raw_logits = outputs[0][0] # Raw output (Logits)

            # 4. Calculate Probabilities (Fixes the "Always 100" bug)
            probabilities = self.softmax(raw_logits)
            top_class_index = np.argmax(probabilities)
            confidence = probabilities[top_class_index]

            # 5. MOCK STRESS CALCULATION (For Testing)
            # Since MobileNet detects objects, not stress, we simulate stress 
            # using image statistics so the dashboard graph moves.
            
            # Heuristic: Average Red Channel Intensity (0-255)
            # Higher red intensity -> Higher "Mock Stress"
            avg_red = np.mean(frame[:, :, 2]) 
            
            # Base score mapped to 0-100 range
            base_score = (avg_red / 255.0) * 100
            
            # Add random jitter so the graph looks "alive" even if you sit still
            jitter = random.randint(-5, 5)
            
            # Clamp between 0 and 100
            final_stress_score = int(max(0, min(100, base_score + jitter)))

            # OPTIONAL: Log for debugging
            # logger.info(f"Class: {top_class_index} | Conf: {confidence:.2f} | Red: {avg_red:.1f} | Stress: {final_stress_score}")

            return OpticalAnalysisResponse(
                status="processed",
                stress_score=final_stress_score,
                is_face_detected=True,
                metadata={
                    "model": "MobileNetV2",
                    "confidence": float(confidence),
                    "simulation_mode": "red_channel_heuristic"
                }
            )

        except Exception as e:
            logger.error(f"Inference Error: {e}")
            return OpticalAnalysisResponse(status="failed", stress_score=0, is_face_detected=False)

# Singleton Instance
optical_analyzer = OpticalAnalyzer()