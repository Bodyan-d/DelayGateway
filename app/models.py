from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import func
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import ForeignKey
from geoalchemy2 import Geometry
from app.db import Base

class Carrier(Base):
    __tablename__ = "carriers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True, index=True)  # stored hashed in prod
    extra_metadata  = Column(JSONB, nullable=True)

class Delay(Base):
    __tablename__ = "delays"
    id = Column(Integer, primary_key=True, index=True)
    carrier = Column(String, index=True)
    line_id = Column(String, index=True)
    vehicle_type = Column(String)
    vehicle_id = Column(String, index=True)
    status = Column(String)  # on_time / delayed / canceled
    delay_minutes = Column(Integer)
    last_update = Column(DateTime(timezone=True), server_default=func.now())
    location = Column(Geometry(geometry_type='POINT', srid=4326))  # PostGIS point
    extra = Column(JSONB, nullable=True)
