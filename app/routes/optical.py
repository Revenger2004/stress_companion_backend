from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.optical_service import optical_analyzer

router = APIRouter()

@router.websocket("/ws/optical")
async def optical_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint strictly for RGB Webcam Stress Analysis.
    Client sends: Binary Blob (JPEG)
    Server sends: JSON (OpticalAnalysisResponse)
    """
    await websocket.accept()
    
    try:
        while True:
            # 1. Receive Binary Blob (Wait for client)
            data = await websocket.receive_bytes()

            # 2. Process via Service Layer
            # For heavy models, wrap this in asyncio.to_thread() to avoid blocking
            result_schema = optical_analyzer.process_frame(data)

            # 3. Send Pydantic Model as JSON
            # This unlocks the frontend's backpressure mechanism
            await websocket.send_json(result_schema.model_dump())

    except WebSocketDisconnect:
        # Normal behavior when user navigates away
        pass
    except Exception as e:
        # Log unexpected connection errors
        print(f"Optical WS Error: {e}")
        try:
            await websocket.close()
        except:
            pass