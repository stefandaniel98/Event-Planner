import threading 
from datetime import datetime, timedelta
from typing import Dict, List
import winsound
import tkinter as tk
from tkinter import messagebox

try:
    from plyer import notification
except ImportError:
    notification = None


from database import Database

class NotificationScheduler: 

    def __init__(self, db: Database):
        '''Initializes the scheduler with the database and prepares the timer storage.'''
        self.db = db
        self.timers: Dict[int, List[threading.Timer]] = {}

    def _notify(self, title: str, message: str):
        '''Sends notification via sound, system tray, or fallback message box.'''
        try: 
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        except Exception:
            pass

        if notification:
            try:
                notification.notify(
                    title=title,
                    message=message,
                    app_name="Event Planner",
                    timeout=10
                )
                return
            except:
                pass

        try:
            popup = tk.Tk()
            popup.withdraw()
            messagebox.showinfo(title, message)
            popup.destroy()
        except:
            print("[ERROR] Could not display notification.")
                  
    def _notify_event(self, ev: dict):
        '''Generates the notification message content.'''
        msg = f"{ev['description']}\nDate: {ev['date']}  Time: {ev['time']}"
        self._notify(f"🔔 Event: {ev['title']}", msg)

    def _schedule_timer(self, delay: float, func, args=()):
        t = threading.Timer(delay, func, args)
        t.daemon = True
        t.start()
        return t
    

    def _schedule_event_alerts(self, event: dict):
        ''' Schedules event notifications based on priority level. '''
        event_id = event["id"]
        self.cancel_event(event_id)
        date_str = event["date"]
        time_str = event["time"]
        event_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        now = datetime.now()


        if event_dt <= now:
            return
        
        self.timers[event_id] = []

        # Map priority strings to number of alerts
        priority = event.get("priority", "Medium")
        priority_map = {
            "Low": 1,
            "Medium": 2,
            "High": 3
        }

        alerts = priority_map.get(priority, 1)

        # Time offsets (in seconds) for each alert level
        offsets = {
            1: [0], # At exact time
            2: [10 * 60, 0], # 10 min before + exact time
            3: [30 * 60, 10 * 60, 0], # 30 min before, 10min before, exact time 
        }

        for offset in offsets.get(alerts, [0]):
            alert_time = event_dt - timedelta(seconds=offset)

            if alert_time <= now:
                continue 

            delay = (alert_time - now).total_seconds()

            t = self._schedule_timer(
                 delay,
                 self._notify_event,
                 args=(event,)
            )
            self.timers[event_id].append(t)


    def schedule_all(self):
        """Schedules alerts for ALL events in the database."""
        events = self.db.list_all()
        for ev in events:
            self._schedule_event_alerts(ev)

    def schedule_event(self, event: dict):
        """Schedules alerts for a single new or edited event."""
        self._schedule_event_alerts(event)

    def cancel_event(self, event_id: int):
        """Cancels all scheduled notifications for a specific event."""
        if event_id in self.timers:
            for t in self.timers[event_id]:
                try:
                    t.cancel()
                except:
                    pass
            self.timers[event_id] = []

    def stop(self):
        """Stops all scheduled notifications."""
        for key in list(self.timers.keys()):
            self.cancel_event(key)