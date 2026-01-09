from sqlalchemy.orm import Session
import models, schemas

def get_rooms(db: Session):
    return db.query(models.Room).all()

def create_room(db: Session, room: schemas.RoomCreate):
    db_room = models.Room(name=room.name)
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room

def delete_room(db: Session, room_id: int):
    db_room = db.query(models.Room).filter(models.Room.id == room_id).first()
    if db_room:
        db.delete(db_room)
        db.commit()
    return db_room

def create_zone(db: Session, zone: schemas.ZoneCreate, room_id: int):
    db_zone = models.Zone(**zone.dict(), room_id=room_id)
    db.add(db_zone)
    db.commit()
    db.refresh(db_zone)
    return db_zone

def update_zone(db: Session, zone_id: int, enabled: bool):
    db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if db_zone:
        db_zone.enabled = enabled
        db.commit()
        db.refresh(db_zone)
    return db_zone

def update_event(db: Session, event_id: int, enabled: bool):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db_event.enabled = enabled
        db.commit()
        db.refresh(db_event)
    return db_event

def create_event(db: Session, event: schemas.EventCreate, zone_id: int):
    db_event = models.Event(**event.dict(), zone_id=zone_id)
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event
