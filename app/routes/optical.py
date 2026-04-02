from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.frame_processing_service import FrameProcessingService
from app.db.session import SessionLocal

router = APIRouter()

@router.websocket("/ws/optical")
async def optical_websocket_endpoint(
    websocket: WebSocket,
    session_id: str | None = Query(None, description="Backend session UUID; required to persist frames"),
):
    """
    WebSocket endpoint strictly for RGB Webcam Stress Analysis.
    Saves frames to disk and predictions to DB if session_id is provided.
    """
    await websocket.accept()
    
    db = SessionLocal()
    processor = FrameProcessingService(session_id=session_id, camera_type="optical", db=db)
    try:
        while True:
            # 1. Receive Binary Blob
            data = await websocket.receive_bytes()

            # 2. Process and Save via Service Layer
            result_schema = processor.process_and_save_frame(data)

            # 3. Return result to frontend
            await websocket.send_json(result_schema.model_dump())

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"Optical WS Error: {e}")
    finally:
        db.close()
        try:
            await websocket.close()
        except:
            pass