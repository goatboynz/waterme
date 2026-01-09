import time
import threading
import datetime
import requests
import os
from sqlalchemy.orm import Session
from database import SessionLocal
import models

SUPERVISOR_TOKEN = os.getenv("SUPERVISOR_TOKEN", "")
HA_URL = "http://supervisor/core/api"

def get_ha_headers():
    return {
        "Authorization": f"Bearer {SUPERVISOR_TOKEN}",
        "Content-Type": "application/json",
    }

def turn_on(entity_id: str):
    url = f"{HA_URL}/services/switch/turn_on"
    if entity_id.startswith("light."):
        url = f"{HA_URL}/services/light/turn_on"
    requests.post(url, json={"entity_id": entity_id}, headers=get_ha_headers())

def turn_off(entity_id: str):
    url = f"{HA_URL}/services/switch/turn_off"
    if entity_id.startswith("light."):
        url = f"{HA_URL}/services/light/turn_off"
    requests.post(url, json={"entity_id": entity_id}, headers=get_ha_headers())

def run_scheduler():
    print("Scheduler started...")
    while True:
        try:
            db = SessionLocal()
            now = datetime.datetime.now()
            current_time = now.strftime("%H:%M")
            current_day = str(now.weekday())

            events = db.query(models.Event).filter(
                models.Event.start_time == current_time,
                models.Event.enabled == True
            ).all()

            for event in events:
                if current_day in event.days.split(","):
                    # Check if zone is also enabled
                    zone = event.zone
                    if zone.enabled:
                        print(f"Triggering event {event.id} for zone {zone.name}")
                        # Trigger irrigation in a separate thread to avoid blocking the scheduler
                        threading.Thread(target=irrigate, args=(zone.pump_entity, zone.solenoid_entity, event.duration)).start()
            
            db.close()
        except Exception as e:
            print(f"Scheduler error: {e}")
        
        # Wait for next minute
        time.sleep(60)

def irrigate(pump_entity: str, solenoid_entity: str, duration: int):
    try:
        # Open solenoid first if exists
        if solenoid_entity:
            turn_on(solenoid_entity)
            time.sleep(1) # Small delay
        
        # Turn on pump
        turn_on(pump_entity)
        
        # Wait for duration
        time.sleep(duration)
        
        # Turn off pump
        turn_off(pump_entity)
        
        # Turn off solenoid if exists
        if solenoid_entity:
            time.sleep(1)
            turn_off(solenoid_entity)
    except Exception as e:
        print(f"Irrigation error: {e}")

def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
