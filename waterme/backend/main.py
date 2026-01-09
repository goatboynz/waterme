from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import models, schemas, crud, database, scheduler
from database import engine, get_db
from typing import List
import requests
import os
import threading

# Initialize database
models.Base.metadata.create_all(bind=engine)

# Start Scheduler
scheduler.start_scheduler()

app = FastAPI(title="WaterMe API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HA API Integration
SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN", "")
HA_URL = "http://supervisor/core/api"

def get_ha_headers():
    return {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

@app.get("/api/ha/entities")
async def get_entities():
    try:
        response = requests.get(f"{HA_URL}/states", headers=get_ha_headers(), timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        # For local development, return mock data if HA is not available
        return [
            {"entity_id": "switch.pump_1", "attributes": {"friendly_name": "Pump 1"}},
            {"entity_id": "switch.solenoid_1", "attributes": {"friendly_name": "Solenoid 1"}},
        ]

@app.get("/api/rooms", response_model=List[schemas.Room])
def read_rooms(db: Session = Depends(get_db)):
    return crud.get_rooms(db)

@app.post("/api/rooms", response_model=schemas.Room)
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    return crud.create_room(db=db, room=room)

@app.delete("/api/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    crud.delete_room(db, room_id)
    return {"status": "success"}

@app.post("/api/rooms/{room_id}/zones", response_model=schemas.Zone)
def create_zone(room_id: int, zone: schemas.ZoneCreate, db: Session = Depends(get_db)):
    return crud.create_zone(db=db, zone=zone, room_id=room_id)

@app.patch("/api/zones/{zone_id}", response_model=schemas.Zone)
def update_zone(zone_id: int, zone: schemas.ZoneUpdate, db: Session = Depends(get_db)):
    return crud.update_zone(db=db, zone_id=zone_id, enabled=zone.enabled)

@app.post("/api/zones/{zone_id}/trigger")
def trigger_zone(zone_id: int, duration: int = 60, db: Session = Depends(get_db)):
    db_zone = db.query(models.Zone).filter(models.Zone.id == zone_id).first()
    if not db_zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    # Trigger irrigation in background
    threading.Thread(target=scheduler.irrigate, args=(db_zone.pump_entity, db_zone.solenoid_entity, duration)).start()
    return {"status": "triggered"}

@app.post("/api/zones/{zone_id}/events", response_model=schemas.Event)
def create_event(zone_id: int, event: schemas.EventCreate, db: Session = Depends(get_db)):
    return crud.create_event(db=db, event=event, zone_id=zone_id)

@app.patch("/api/events/{event_id}", response_model=schemas.Event)
def update_event(event_id: int, event: schemas.EventUpdate, db: Session = Depends(get_db)):
    return crud.update_event(db=db, event_id=event_id, enabled=event.enabled)

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
