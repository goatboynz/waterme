from pydantic import BaseModel
from typing import List, Optional

class EventBase(BaseModel):
    type: str
    start_time: str
    duration: int
    days: str
    enabled: bool = True

class EventUpdate(BaseModel):
    enabled: bool

class ZoneUpdate(BaseModel):
    enabled: bool

class Event(EventBase):
    id: int
    zone_id: int
    class Config:
        from_attributes = True

class ZoneBase(BaseModel):
    name: str
    pump_entity: str
    solenoid_entity: Optional[str] = None
    enabled: bool = True

class ZoneCreate(ZoneBase):
    pass

class Zone(ZoneBase):
    id: int
    room_id: int
    events: List[Event] = []
    class Config:
        from_attributes = True

class RoomBase(BaseModel):
    name: str

class RoomCreate(RoomBase):
    pass

class Room(RoomBase):
    id: int
    zones: List[Zone] = []
    class Config:
        from_attributes = True
