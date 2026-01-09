from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    zones = relationship("Zone", back_populates="room", cascade="all, delete-orphan")

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    pump_entity = Column(String)  # HA entity_id
    solenoid_entity = Column(String, nullable=True)  # HA entity_id
    enabled = Column(Boolean, default=True)
    room = relationship("Room", back_populates="zones")
    events = relationship("Event", back_populates="zone", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"))
    type = Column(String)  # "p1" or "p2"
    start_time = Column(String)  # HH:MM
    duration = Column(Integer)  # seconds
    days = Column(String)  # "0,1,2,3,4,5,6" (Mon-Sun)
    enabled = Column(Boolean, default=True)
    zone = relationship("Zone", back_populates="events")
