from sqlalchemy.orm import Session
from app.services.storage_service import save_frame_and_prediction

class FrameProcessingService:
    """
    Service Layer that encapsulates logic for processing incoming raw frames from websockets.
    Validates stream type, delegates to the appropriate ML inference engine, tracks metadata,
    and handles saving the frame to disk and its inference results to the database.
    """

    def __init__(self, session_id: str | None, camera_type: str, db: Session):
        self.session_id = session_id
        self.camera_type = camera_type
        self.db = db
        self.frame_count = 0

        # Inject the correct analyzer tool dynamically based on enum string
        if camera_type == "optical":
            from app.services.optical_service import optical_analyzer
            self.analyzer = optical_analyzer
        elif camera_type == "thermal":
            from app.services.thermal_service import thermal_analyzer
            self.analyzer = thermal_analyzer
        else:
            raise ValueError(f"Unsupported camera type: {camera_type}")

    def process_and_save_frame(self, data: bytes):
        """
        1. Forward frame binary to ML Model
        2. Store to File System/DB if session_id is active
        3. Returns the prediction schema
        """
        # 1. Process Frame via ML tools
        result_schema = self.analyzer.process_frame(data)

        # 2. Save Data & Prediction to Disk + Db
        if self.session_id:
            self.frame_count += 1
            save_frame_and_prediction(
                db=self.db,
                session_id=self.session_id,
                camera_type=self.camera_type,
                frame_count=self.frame_count,
                data=data,
                stress_probability=result_schema.stress_probability,
            )

        # 3. Yield to WebSocket response line
        return result_schema
