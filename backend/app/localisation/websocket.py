from fastapi import WebSocket

async def ws_localisation(websocket: WebSocket, groupe_id: str, token: str):
    await websocket.accept()
    await websocket.send_json({"t": "bienvenue", "groupe_id": groupe_id})
    await websocket.close()