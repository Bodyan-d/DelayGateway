import uvicorn
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.auth import verify_jwt, create_jwt_for_carrier, get_carrier_by_api_key
from app.schemas import DelayCreate, DelayOut
from app.db import get_db, engine, Base, AsyncSessionLocal
from app import crud
from app.ws_manager import ws_manager
import asyncio
import redis.asyncio as redis
from app.tasks import publish_delay, redis_listener, REDIS_CHANNEL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Carrier

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup: create tables (for dev/demo only)
@app.on_event("startup")
async def startup():
    # create DB tables (in prod use migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # start redis listener
    loop = asyncio.get_event_loop()
    loop.create_task(redis_listener())

# Endpoint for carriers to exchange api_key -> JWT (simple)
@app.post("/api/auth/token")
async def issue_token(api_key: str, db: AsyncSession = Depends(get_db)):
    # For demo: accepts api_key in body
    stmt = select(Carrier).where(Carrier.api_key == api_key)
    res = await db.execute(stmt)
    carrier = res.scalar_one_or_none()
    if not carrier:
        raise HTTPException(status_code=401, detail="Invalid api_key")
    token = create_jwt_for_carrier(carrier_id=carrier.id, carrier_name=carrier.name)
    return {"token": token}

# Endpoint for carriers to post delays (requires JWT)
@app.post("/api/delays/", response_model=dict)
async def receive_delay(payload: DelayCreate, token=Depends(verify_jwt), db: AsyncSession = Depends(get_db)):
    # token contains carrier data if valid
    # Optionally enforce that payload.carrier matches token.carrier_name
    if token.carrier_name and payload.carrier != token.carrier_name:
        raise HTTPException(status_code=403, detail="Carrier mismatch")

    delay_id = await crud.create_delay(db, payload)

    # Publish to Redis so other components (WS server / push sender) know
    redis_client = redis.from_url("redis://redis", decode_responses=True)

    event = {
        "type": "delay.new",
        "id": delay_id,
        "carrier": payload.carrier,
        "line_id": payload.line_id,
        "vehicle_id": payload.vehicle_id,
        "status": payload.status,
        "delay_minutes": payload.delay_minutes,
        "last_update": str(payload.last_update),
        "location": {"lat": payload.latitude, "lng": payload.longitude},
        "extra": payload.extra
    }
    await publish_delay(redis_client, event)
    await redis_client.close()

    return {"status": "ok", "id": delay_id}

# Public endpoint for app to fetch recent delays
@app.get("/api/delays/recent", response_model=list[DelayOut])
async def get_recent(db: AsyncSession = Depends(get_db)):
    rows = await crud.list_recent_delays(db, limit=100)
    # map to DelayOut
    out = []
    for r in rows:
        out.append({
            "id": r["id"],
            "carrier": r["carrier"],
            "line_id": r["line_id"],
            "vehicle_type": r["vehicle_type"],
            "vehicle_id": r["vehicle_id"],
            "status": r["status"],
            "delay_minutes": r["delay_minutes"],
            "last_update": r["last_update"],
            "location": {"lat": r["location"]["lat"], "lng": r["location"]["lng"]},
            "extra": r["extra"]
        })
    return out

# WebSocket for real-time updates
@app.websocket("/ws/updates")
async def websocket_updates(ws: WebSocket):
    await ws_manager.connect(ws, topic="global")
    try:
        while True:
            # keep connection alive; optionally receive subscription messages
            data = await ws.receive_text()
            # optional: parse subscription preferences, e.g., area bounding box
            # for demo we ignore incoming messages and only broadcast server events
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
