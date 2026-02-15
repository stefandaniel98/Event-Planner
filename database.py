import sqlite3
from pathlib import Path
from datetime import datetime
'''Establishes the database connection and initializes the schema.'''
DB_FILE = Path(__file__).parent / "events.db"

class Database:
    def __init__(self, db_path: Path | str = DB_FILE):
        '''Internal method to create the "events" table if it doesn't exist.'''
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()


    def _init_schema(self):
        '''Internal method to create the "events" table if it doesn't exist.'''
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            priority TEXT CHECK(priority IN ('High', 'Medium', 'Low'))DEFAULT 'Medium',
            alerts INTEGER DEFAULT 1,
            last_alert_sent TEXT
            );"""
        )
        self.conn.commit()


    def add_event(self,data: dict) -> int:
        '''Adds a new event to the database.'''
        cur = self.conn.cursor()
        cur.execute(
            """
            
            INSERT INTO events(title, description, date, time, priority)
            VALUES(?,?,?,?,?)
            """,
            (
                data.get("title"),
                data.get("description"),
                data.get("date"),
                data.get("time"),
                data.get("priority", "Medium"),
            ),
        )
        self.conn.commit()
        return cur.lastrowid
    

    def update_event(self, event_id: int, data: dict):
        '''Updates an existing event's information based on its ID.'''
        cur = self.conn.cursor()
        cur.execute(

            """
            UPDATE events
                SET title=?, description=?, date=?, time=?, priority=?
                WHERE id=?

            """,
            (
                data.get("title"),
                data.get("description"),
                data.get("date"),
                data.get("time"),
                data.get("priority", "Medium"),
                event_id,
            ),
        )
        self.conn.commit()
    
    
    def delete_event(self, event_id: int):
        '''Deletes an event from the database by ID.'''
        cur = self.conn.cursor()
        cur.execute("DELETE FROM events WHERE id=?", (event_id,))
        self.conn.commit()

    
    def get_event(self, event_id: int):
        '''Returns a single event based on its ID.'''
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM events WHERE id=?", (event_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    
    
    def list_events_by_date(self, date_str: str) -> list[dict]:
        '''Lists all events for a specific date, ordered by time and priority.'''
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM events
            WHERE date=?
            ORDER BY time ASC,
                     CASE priority
                         WHEN 'High' THEN 3
                         WHEN 'Medium' THEN 2
                         WHEN 'Low' THEN 1
                     END DESC
            """,
            (date_str,),
        )
        return [dict(r) for r in cur.fetchall()]
    
    
    def list_all(self) -> list[dict]:
        '''Lists all existing events in the database ordered by date and time.'''
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM events ORDER BY date ASC, time ASC")
        return [dict(r) for r in cur.fetchall()]
    

    def list_in_next_hours(self, now_iso: str, until_iso: str) -> list[dict]:
        '''Lists events occurring within a specified time range (ISO format).'''
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT *
            FROM events
            WHERE datetime(substr(date,1,10) || ' ' ||
                       substr(time,1,5)) 
              BETWEEN datetime(?) AND datetime(?)
            ORDER BY date ASC, time ASC
            """,
            (now_iso, until_iso),
        )
        
        return [dict(r) for r in cur.fetchall()]
    

    def mark_alert_sent_today(self, event_id: int):
        '''Updates the last_alert_sent column with today's date for a specific event.'''
        today = datetime.now().strftime("%Y-%m-%d")
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE events SET last_alert_sent=? WHERE id=?",
            (today, event_id),
        )
        self.conn.commit()

    
    def days_with_events(self) -> set[str]:
        '''Returns a set of all dates that have registered events.'''
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT date FROM events")
        return {r[0] for r in cur.fetchall()}
    
    def close(self):
        '''Closes the database connection. Recommended at the end of the session.'''
        self.conn.close()