import { useState, useEffect } from 'react';
import './App.css';

interface HAEntity {
  entity_id: string;
  attributes: {
    friendly_name?: string;
  };
}

interface Event {
  id: number;
  type: string;
  start_time: string;
  duration: number;
  days: string;
  enabled: boolean;
}

interface Zone {
  id: number;
  name: string;
  pump_entity: string;
  solenoid_entity?: string;
  enabled: boolean;
  events: Event[];
}

interface Room {
  id: number;
  name: string;
  zones: Zone[];
}

const API_BASE = '/api';

function App() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [entities, setEntities] = useState<HAEntity[]>([]);
  const [showAddRoom, setShowAddRoom] = useState(false);
  const [newRoomName, setNewRoomName] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [roomsRes, entitiesRes] = await Promise.all([
        fetch(`${API_BASE}/rooms`),
        fetch(`${API_BASE}/ha/entities`)
      ]);
      const roomsData = await roomsRes.json();
      const entitiesData = await entitiesRes.json();
      setRooms(roomsData);
      setEntities(entitiesData);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  const addRoom = async () => {
    if (!newRoomName) return;
    await fetch(`${API_BASE}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: newRoomName })
    });
    setNewRoomName('');
    setShowAddRoom(false);
    fetchData();
  };

  const deleteRoom = async (id: number) => {
    if (!confirm('Are you sure you want to delete this room?')) return;
    await fetch(`${API_BASE}/rooms/${id}`, { method: 'DELETE' });
    fetchData();
  };

  if (loading) return <div className="loading">Initializing WaterMe...</div>;

  return (
    <div className="container">
      <header className="header glass-card">
        <div className="logo">
          <span className="icon">ÃƒÆ’Ã‚Â°Ãƒâ€¦Ã‚Â¸ÃƒÂ¢Ã¢â€šÂ¬Ã¢â€žÂ¢Ãƒâ€šÃ‚Â§</span>
          <h1>WaterMe</h1>
        </div>
        <button className="btn-primary" onClick={() => setShowAddRoom(true)}>+ Add Room</button>
      </header>

      <main className="dashboard">
        {rooms.map(room => (
          <RoomCard key={room.id} room={room} entities={entities} onUpdate={fetchData} onDelete={() => deleteRoom(room.id)} />
        ))}
      </main>

      {showAddRoom && (
        <div className="modal-overlay">
          <div className="modal glass-card">
            <h2>Add New Room</h2>
            <input
              type="text"
              placeholder="Room Name (e.g. Flower Room 1)"
              value={newRoomName}
              onChange={(e) => setNewRoomName(e.target.value)}
            />
            <div className="modal-actions">
              <button onClick={() => setShowAddRoom(false)}>Cancel</button>
              <button className="btn-primary" onClick={addRoom}>Create</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function RoomCard({ room, entities, onUpdate, onDelete }: { room: Room, entities: HAEntity[], onUpdate: () => void, onDelete: () => void }) {
  const [showAddZone, setShowAddZone] = useState(false);
  const [newZone, setNewZone] = useState({ name: '', pump_entity: '', solenoid_entity: '' });

  const addZone = async () => {
    await fetch(`${API_BASE}/rooms/${room.id}/zones`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newZone)
    });
    setShowAddZone(false);
    setNewZone({ name: '', pump_entity: '', solenoid_entity: '' });
    onUpdate();
  };

  const toggleZone = async (zoneId: number, enabled: boolean) => {
    await fetch(`${API_BASE}/zones/${zoneId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    onUpdate();
  };

  const triggerZone = async (zoneId: number) => {
    await fetch(`${API_BASE}/zones/${zoneId}/trigger`, { method: 'POST' });
    alert('Manual irrigation triggered!');
  };

  return (
    <div className="room-card glass-card">
      <div className="room-header">
        <h3>{room.name}</h3>
        <button className="btn-text" onClick={onDelete}>Delete</button>
      </div>

      <div className="zones-list">
        {room.zones.map(zone => (
          <ZoneItem
            key={zone.id}
            zone={zone}
            entities={entities}
            onUpdate={onUpdate}
            onToggle={(enabled) => toggleZone(zone.id, enabled)}
            onTrigger={() => triggerZone(zone.id)}
          />
        ))}
      </div>

      <button className="btn-outline" onClick={() => setShowAddZone(true)}>+ Add Zone</button>

      {showAddZone && (
        <div className="modal-overlay">
          <div className="modal glass-card">
            <h2>Add Zone to {room.name}</h2>
            <input
              placeholder="Zone Name"
              value={newZone.name}
              onChange={e => setNewZone({ ...newZone, name: e.target.value })}
            />
            <select value={newZone.pump_entity} onChange={e => setNewZone({ ...newZone, pump_entity: e.target.value })}>
              <option value="">Select Pump Entity</option>
              {entities.map(e => <option key={e.entity_id} value={e.entity_id}>{e.attributes.friendly_name || e.entity_id}</option>)}
            </select>
            <select value={newZone.solenoid_entity} onChange={e => setNewZone({ ...newZone, solenoid_entity: e.target.value })}>
              <option value="">Select Solenoid (Optional)</option>
              {entities.map(e => <option key={e.entity_id} value={e.entity_id}>{e.attributes.friendly_name || e.entity_id}</option>)}
            </select>
            <div className="modal-actions">
              <button onClick={() => setShowAddZone(false)}>Cancel</button>
              <button className="btn-primary" onClick={addZone}>Add Zone</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ZoneItem({ zone, onUpdate, onToggle, onTrigger }: { zone: Zone, entities: HAEntity[], onUpdate: () => void, onToggle: (enabled: boolean) => void, onTrigger: () => void }) {
  const [showEvents, setShowEvents] = useState(false);
  const [newEvent, setNewEvent] = useState({ type: 'p1', start_time: '08:00', duration: 60, days: '0,1,2,3,4,5,6' });

  const addEvent = async () => {
    await fetch(`${API_BASE}/zones/${zone.id}/events`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newEvent)
    });
    onUpdate();
  };

  const toggleEvent = async (eventId: number, enabled: boolean) => {
    await fetch(`${API_BASE}/events/${eventId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ enabled })
    });
    onUpdate();
  };

  return (
    <div className={`zone-item ${!zone.enabled ? 'disabled' : ''}`}>
      <div className="zone-info">
        <div className="zone-main">
          <label className="switch">
            <input type="checkbox" checked={zone.enabled} onChange={(e) => onToggle(e.target.checked)} />
            <span className="slider round"></span>
          </label>
          <span className="zone-name">{zone.name}</span>
        </div>
        <div className="zone-actions">
          <button className="btn-mini btn-run" onClick={onTrigger} disabled={!zone.enabled}>Run Now</button>
          <button className="btn-mini" onClick={() => setShowEvents(!showEvents)}>
            {zone.events.length} Events {showEvents ? 'ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“Ãƒâ€šÃ‚Â´' : 'ÃƒÆ’Ã‚Â¢ÃƒÂ¢Ã¢â€šÂ¬Ã¢â‚¬Å“Ãƒâ€šÃ‚Â¾'}
          </button>
        </div>
      </div>

      {showEvents && (
        <div className="events-panel">
          {zone.events.map(event => (
            <div key={event.id} className={`event-row ${!event.enabled ? 'disabled' : ''}`}>
              <div className="event-main">
                <input type="checkbox" checked={event.enabled} onChange={(e) => toggleEvent(event.id, e.target.checked)} />
                <span className="event-type">{event.type.toUpperCase()}</span>
                <span>{event.start_time}</span>
                <span>{event.duration}s</span>
              </div>
              <span className="event-days">{event.days.split(',').length === 7 ? 'Daily' : 'Custom'}</span>
            </div>
          ))}
          <div className="add-event-form">
            <select value={newEvent.type} onChange={e => setNewEvent({ ...newEvent, type: e.target.value })}>
              <option value="p1">P1</option>
              <option value="p2">P2</option>
            </select>
            <input type="time" value={newEvent.start_time} onChange={e => setNewEvent({ ...newEvent, start_time: e.target.value })} />
            <input type="number" placeholder="Sec" value={newEvent.duration} onChange={e => setNewEvent({ ...newEvent, duration: parseInt(e.target.value) })} />
            <button onClick={addEvent}>+</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
