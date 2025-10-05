from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from jwt import PyJWTError
from datetime import datetime, timedelta
from app.config import settings
from app.schemas import TokenData
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Carrier
from app.db import AsyncSessionLocal

security = HTTPBearer()

def create_jwt_for_carrier(carrier_id: int, carrier_name: str):
    now = datetime.utcnow()
    payload = {
        "sub": str(carrier_id),
        "name": carrier_name,
        "iat": now.timestamp(),
        "exp": (now + timedelta(seconds=settings.JWT_EXPIRES_SECONDS)).timestamp()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token

async def verify_jwt(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        carrier_id = int(payload.get("sub"))
        carrier_name = payload.get("name")
        return TokenData(carrier_id=carrier_id, carrier_name=carrier_name)
    except PyJWTError:
        raise HTTPException(status_code=403, detail="Invalid token")

# utility for login by api_key (for issuing token) - simple example
async def get_carrier_by_api_key(api_key: str, db: AsyncSession):
    stmt = select(Carrier).where(Carrier.api_key == api_key)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()

