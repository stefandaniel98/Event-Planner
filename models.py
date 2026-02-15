from datetime import datetime
from database import Database
from utils import combine, human_countdown

class EventManager:
    def __init__(self, db: Database):
        """Initializes the manager with a database instance."""
        self.db = db

    def add(self, title, description, date, time, priority):
        """Creates a new event and saves it to the database."""
        return self.db.add_event({
            "title": title,
            "description": description,
            "date": date,
            "time": time,
            "priority": priority,
        })

    def update(self, event_id, **kwargs):
        """Updates an existing event identified by its event_id."""
        self.db.update_event(event_id, kwargs)

    def delete(self, event_id):
        """Deletes an event from the database by its ID."""
        self.db.delete_event(event_id)

    def events_on(self, date_str):
        """Returns all events scheduled for a specific date."""
        return self.db.list_events_by_date(date_str)
    
    def next_up_in(self, hours: int = 3):
        """Returns all events occurring within the next specified hours."""
        from utils import now_iso_minute, in_hours_iso
        return self.db.list_in_next_hours(now_iso_minute(), in_hours_iso(hours))
    
    def countdown_for(self, event: dict) -> str:
        """Calculates the time remaining until the event and returns a human-readable string."""
        dt = combine(event["date"], event["time"]) - datetime.now()
        return human_countdown(dt)
        