from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from app.models import Delay, Carrier
from app.schemas import DelayCreate
from sqlalchemy import text
import datetime
import json

async def create_delay(db: AsyncSession, delay: DelayCreate):
    # Use raw SQL for PostGIS geometry insertion
    sql = text("""
        INSERT INTO delays (carrier, line_id, vehicle_type, vehicle_id, status, delay_minutes, last_update, location, extra)
        VALUES (:carrier, :line_id, :vehicle_type, :vehicle_id, :status, :delay_minutes, :last_update,
                ST_SetSRID(ST_MakePoint(:lng, :lat), 4326), :extra)
        RETURNING id
    """)
    params = {
        "carrier": delay.carrier,
        "line_id": delay.line_id,
        "vehicle_type": delay.vehicle_type,
        "vehicle_id": delay.vehicle_id,
        "status": delay.status,
        "delay_minutes": delay.delay_minutes,
        "last_update": delay.last_update,
        "lng": delay.longitude,
        "lat": delay.latitude,
        "extra": json.dumps(delay.extra) if delay.extra else None
    }
    result = await db.execute(sql, params)
    await db.commit()
    row = result.first()
    if row:
        return row[0]
    return None

async def list_recent_delays(db: AsyncSession, limit: int = 100):
    stmt = text("""
        SELECT id, carrier, line_id, vehicle_type, vehicle_id, status, delay_minutes, last_update,
               ST_X(ST_AsText(location)) as lng,
               ST_Y(ST_AsText(location)) as lat,
               extra
        FROM delays
        ORDER BY last_update DESC
        LIMIT :limit
    """)
    res = await db.execute(stmt, {"limit": limit})
    rows = res.fetchall()
    out = []
    for r in rows:
        out.append({
            "id": r[0],
            "carrier": r[1],
            "line_id": r[2],
            "vehicle_type": r[3],
            "vehicle_id": r[4],
            "status": r[5],
            "delay_minutes": r[6],
            "last_update": r[7],
            "location": {"lng": r[8], "lat": r[9]},
            "extra": r[10]
        })
    return out
