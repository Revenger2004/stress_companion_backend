from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.services.optical_service import optical_analyzer
from app.services.storage_service import save_frame_and_prediction
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
    frame_count = 0
    try:
        while True:
            # 1. Receive Binary Blob
            data = await websocket.receive_bytes()

            # 2. Process via Service Layer
            result_schema = optical_analyzer.process_frame(data)

            # 3. Save to DB/Disk if Session Active
            if session_id:
                frame_count += 1
                save_frame_and_prediction(
                    db=db,
                    session_id=session_id,
                    camera_type="optical",
                    frame_count=frame_count,
                    data=data,
                    stress_probability=result_schema.stress_probability
                )

            # 4. Return result to frontend
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