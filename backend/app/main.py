from fastapi import FastAPI, WebSocket, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 SafeTrack démarre...")
    await init_db()
    print("✅ Redis en attente (optionnel)")
    print("📖 Docs : http://localhost:8000/docs")
    yield
    print("🔴 SafeTrack arrêté")

app = FastAPI(title="SafeTrack API", version="2.0.0", lifespan=lifespan)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Routers
from app.auth.router import router as auth_router
from app.groupes.router import router as groupes_router
from app.localisation.router import router as localisation_router
from app.alertes.router import router as alertes_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(groupes_router, prefix="/api/v1/groupes", tags=["Groupes"])
app.include_router(localisation_router, prefix="/api/v1/localisation", tags=["Localisation"])
app.include_router(alertes_router, prefix="/api/v1/alertes", tags=["Alertes"])

# WebSocket
from app.localisation.websocket import ws_localisation
@app.websocket("/ws/localisation/{groupe_id}")
async def websocket_localisation(websocket: WebSocket, groupe_id: str, token: str = Query(...)):
    await ws_localisation(websocket, groupe_id, token)

@app.get("/")
async def racine():
    return {"app": "SafeTrack", "version": "2.0.0", "status": "✅ En ligne", "docs": "/docs"}