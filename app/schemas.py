from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class DelayCreate(BaseModel):
    carrier: str
    line_id: str
    vehicle_type: str
    vehicle_id: str
    status: str
    delay_minutes: int
    last_update: datetime
    latitude: float
    longitude: float
    extra: Optional[dict] = None

class DelayOut(BaseModel):
    id: int
    carrier: str
    line_id: str
    vehicle_type: str
    vehicle_id: str
    status: str
    delay_minutes: int
    last_update: datetime
    location: dict
    extra: Optional[dict]

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    carrier_id: Optional[int]
    carrier_name: Optional[str]
