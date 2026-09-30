import enum
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum as SqlEnum,
)

from sqlalchemy.orm import relationship
from database import Base

#lol just makes getting the time easier
def utcnow():
    return datetime.now(timezone.utc)

class UserRole(enum.Enum):
    resident = "resident"
    operator = "operator"
    admin = "admin"

class DroneStatus(enum.Enum):
    idle = "idle"
    in_flight = "in_flight"
    charging = "charging"
    maintenance = "maintenance"
    offline = "offline"

class PadStatus(enum.Enum):
    free = "free"
    reserved = "reserved"
    occupied = "occupied"
    maintenance = "maintenance"

class ChargerStatus(enum.Enum):
    free = "free"
    occupied = "occupied"
    fault = "fault"
    maintenance = "maintenance"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(SqlEnum(UserRole), nullable=False, default=UserRole.resident)
    created_at = Column(DateTime, default=utcnow)

    def to_dict(self):
        return{
            "id": self.id, "username": self.username, "email": self.email, "password_hash": self.password_hash, "role":self.role, "created_at": self.created_at
        }

class Drone(Base):
    __tablename__ = "drones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    model = Column(String(100), nullable=True)
    status = Column(SqlEnum(DroneStatus), nullable=False, default=DroneStatus.idle)
    battery_pct = Column(Float, nullable=False, default=100.0)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    owned_by_city = Column(Boolean, nullable=False, default=True)

    current_pad_id = Column(Integer, ForeignKey("landing_pads.id"), nullable=True)
    current_charger_id = Column(Integer, ForeignKey("charging_stations.id"), nullable=True)

    last_seen = Column(DateTime, default=utcnow, onupdate=utcnow)
    created_at = Column(DateTime, default=utcnow)

    current_pad = relationship("LandingPad", foreign_keys=[current_pad_id])
    current_charger = relationship("ChargingStation", foreign_keys=[current_charger_id])

    def to_dict(self):
        return{
            "id": self.id,"name": self.name, "model": self.model,"status": self.status.value,"battery_pct": self.battery_pct,"current_latitude": self.current_latitude,"current_longitude": self.current_longitude,"owned_by_city": self.owned_by_city,
            "current_pad_id": self.current_pad_id, "current_charger_id": self.current_charger_id,"last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }

class LandingPad(Base):
    __tablename__ = "landing_pads"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False, default=1)
    status = Column(SqlEnum(PadStatus), nullable=False, default=PadStatus.free)
    created_at = Column(DateTime, default=utcnow)
    charging_stations = relationship("ChargingStation", back_populates = "pad") #provides option to give it more than 1 charging station

    def to_dict(self):
        return {
            "id": self.id, "name": self.name, "latitude": self.latitude,"longitude": self.longitude, "capacity": self.capacity, "status": self.status.value,
        }

class ChargingStation(Base):
    __tablename__ = "charging_stations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pad_id = Column(Integer, ForeignKey("landing_pads.id"), nullable=True) #could not be tied to a landing pad
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    charger_type = Column(String(50), nullable=False, default="contact_pad")
    status = Column(SqlEnum(ChargerStatus), nullable=False, default=ChargerStatus.free)
    created_at = Column(DateTime, default=utcnow)

    pad = relationship("LandingPad", back_populates="charging_stations")

    def to_dict(self):
        return {
            "id": self.id,"pad_id": self.pad_id,"latitude": self.latitude,"longitude": self.longitude,"charger_type": self.charger_type,"status": self.status.value,
        }