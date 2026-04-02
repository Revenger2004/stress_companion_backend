import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.db_models.domain import Frame, Prediction

STORAGE_BASE = "storage/sessions"

def save_frame_and_prediction(
    db: Session,
    session_id: str,
    camera_type: str,
    frame_count: int,
    data: bytes,
    stress_probability: float
):
    """
    Saves the image binary to disk and writes the metadata and prediction to the database.
    """
    try:
        # Ensure directory exists
        session_dir = f"{STORAGE_BASE}/{session_id}/{camera_type}"
        os.makedirs(session_dir, exist_ok=True)

        # Save Image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filepath = f"{session_dir}/frame_{timestamp}.jpg"
        with open(filepath, "wb") as f:
            f.write(data)

        # Save Metadata
        frame = Frame(
            session_id=session_id,
            camera_type=camera_type,
            frame_number=frame_count,
            image_path=filepath,
            timestamp=datetime.utcnow()
        )
        db.add(frame)
        db.flush()

        prediction = Prediction(
            frame_id=frame.frame_id,
            model_type=camera_type,
            stress_probability=stress_probability
        )
        db.add(prediction)
        db.commit()
    except Exception as save_err:
        print(f"Failed to save {camera_type} frame: {save_err}")
        db.rollback()