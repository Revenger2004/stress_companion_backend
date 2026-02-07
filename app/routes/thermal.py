from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.thermal_service import thermal_analyzer

router = APIRouter()

@router.websocket("/ws/thermal")
async def thermal_websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint strictly for Thermal Camera Stress Analysis.
    Client sends: Binary Blob (JPEG/PNG representing thermal data)
    Server sends: JSON (ThermalAnalysisResponse)
    """
    await websocket.accept()
    
    try:
        while True:
            # 1. Receive Binary Blob (Wait for client)
            data = await websocket.receive_bytes()

            # 2. Process via Service Layer
            # This calls the process_frame method we wrote in thermal_service.py
            result_schema = thermal_analyzer.process_frame(data)

            # 3. Send Pydantic Model as JSON
            # This returns the ThermalAnalysisResponse (stress_probability, is_stressed, etc.)
            await websocket.send_json(result_schema.model_dump())

    except WebSocketDisconnect:
        # Normal behavior when user navigates away
        pass
    except Exception as e:
        # Log unexpected connection errors
        print(f"Thermal WS Error: {e}")
        try:
            await websocket.close()
        except:
            pass