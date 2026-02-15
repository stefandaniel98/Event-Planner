# test_notif.py
from database import Database
from notifications import NotificationScheduler

# Initialize the database connection
db = Database()

# Mock event for testing purposes
fake_event = {
    "id": 999,
    "title": "Test Notification",
    "description": "This is a test notification for the Event Planner app!",
    "date": "2026-2-30",
    "time": "00:00"
}

# Initialize the scheduler without loading all existing database events
notif = NotificationScheduler(db)

# Trigger the notification instantly to verify the system works
notif._notify_event(fake_event)

print("Test notification sent successfully!")
