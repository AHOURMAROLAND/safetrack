# SafeTrack v2.0

Application mobile anti-enlèvement avec géolocalisation
communautaire en temps réel pour l'Afrique subsaharienne.

## Stack

- Backend : FastAPI + SQLAlchemy + SQLite (dev) / PostgreSQL (prod)
- WebSocket : FastAPI natif
- Frontend : React Native Expo
- Notifications : Firebase FCM + Africa's Talking SMS

## Lancer le backend

```powershell
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

## Architecture

```
backend/app/
├── auth/          → User, JWT, OTP
├── groupes/       → Groupe, Membership
├── localisation/  → GPS, Destination, WebSocket
├── alertes/       → SOS, Audio
└── notifications/ → FCM, SMS
```

## Progression

- [x] T1 — Structure
- [x] T2 — Setup FastAPI
- [x] T3 — Auth JWT
- [x] T4 — Groupes
- [ ] T5 — Localisation + WebSocket
- [ ] T6 — Alertes + Audio
- [ ] T7 — Notifications
- [ ] T8-T12 — Frontend
