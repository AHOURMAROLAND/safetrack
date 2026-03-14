from typing import Optional
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.connexions: dict = {}

    async def connecter(self, websocket: WebSocket, groupe_id: str, user_id: str, nom: str):
        await websocket.accept()
        if groupe_id not in self.connexions:
            self.connexions[groupe_id] = []
        self.connexions[groupe_id].append({"ws": websocket, "user_id": user_id, "nom": nom})

    def deconnecter(self, websocket: WebSocket, groupe_id: str):
        if groupe_id in self.connexions:
            self.connexions[groupe_id] = [
                c for c in self.connexions[groupe_id] if c["ws"] != websocket
            ]

    async def diffuser(self, groupe_id: str, message: dict, exclure: Optional[WebSocket] = None):
        if groupe_id not in self.connexions:
            return
        morts = []
        for c in self.connexions[groupe_id]:
            if c["ws"] == exclure:
                continue
            try:
                await c["ws"].send_json(message)
            except Exception:
                morts.append(c)
        for m in morts:
            self.connexions[groupe_id].remove(m)

    def membres_connectes(self, groupe_id: str) -> list:
        return [{"user_id": c["user_id"], "nom": c["nom"]} for c in self.connexions.get(groupe_id, [])]

manager = ConnectionManager()