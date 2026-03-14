from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select, and_
from app.ws_manager import manager
from app.security import decoder_token
from app.database import AsyncSessionLocal


async def ws_localisation(websocket: WebSocket, groupe_id: str, token: str):
    # Auth
    payload = decoder_token(token)
    if not payload:
        await websocket.close(code=4001)
        return

    user_id = payload.get("sub")

    # Verifier membership
    async with AsyncSessionLocal() as db:
        from app.groupes.models import Membership
        from app.auth.models import User
        result = await db.execute(
            select(Membership).where(and_(
                Membership.user_id == user_id,
                Membership.groupe_id == groupe_id,
                Membership.statut == "approved"
            ))
        )
        if not result.scalar_one_or_none():
            await websocket.close(code=4003)
            return
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        nom = f"{user.prenom} {user.nom}" if user else "Inconnu"

    await manager.connecter(websocket, groupe_id, user_id, nom)

    # Informer le groupe
    await manager.diffuser(groupe_id, {
        "t": "connexion",
        "user_id": user_id,
        "nom": nom,
        "membres_en_ligne": manager.membres_connectes(groupe_id),
    }, exclure=websocket)

    # Bienvenue
    await websocket.send_json({
        "t": "bienvenue",
        "user_id": user_id,
        "membres_en_ligne": manager.membres_connectes(groupe_id),
    })

    try:
        while True:
            data = await websocket.receive_json()
            t = data.get("t")

            if t == "p":
                # Sauvegarder + diffuser position
                async with AsyncSessionLocal() as db:
                    from app.localisation.service import sauvegarder_position
                    await sauvegarder_position(user_id, groupe_id, data, db)
                await manager.diffuser(groupe_id, {
                    "t": "p",
                    "user_id": user_id,
                    "nom": nom,
                    "la": data.get("la"),
                    "lo": data.get("lo"),
                    "v": data.get("v", 0),
                    "m": data.get("m", 0),
                    "b": data.get("b", 100),
                    "ts": datetime.utcnow().isoformat(),
                }, exclure=websocket)

            elif t == "sos":
                await manager.diffuser(groupe_id, {
                    "t": "sos",
                    "user_id": user_id,
                    "nom": nom,
                    "la": data.get("la"),
                    "lo": data.get("lo"),
                    "ts": datetime.utcnow().isoformat(),
                })

            elif t == "ping":
                await websocket.send_json({"t": "pong"})

    except WebSocketDisconnect:
        manager.deconnecter(websocket, groupe_id)
        await manager.diffuser(groupe_id, {
            "t": "deconnexion",
            "user_id": user_id,
            "nom": nom,
            "membres_en_ligne": manager.membres_connectes(groupe_id),
        })