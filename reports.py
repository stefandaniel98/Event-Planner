import csv
import json
from pathlib import Path
from database import Database

def export_csv(db: Database, filepath: Path | str):
    """Exports all events from the database to a CSV file."""
    rows = db.list_all() 

    if not rows:
        
        headers = ["id","title","description","date","time","priority","alerts","last_alert_sent"]
    else:
        headers = list(rows[0].keys())
    with open(filepath, "w", newline='', encoding="utf-8") as f:
        
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for r in rows:
            writer.writerow(r) 


def import_csv(db: Database, filepath: Path | str):
    with open(filepath, newline='', encoding="utf-8") as f:
        """Imports events from a CSV file and adds them to the database."""
        reader = csv.DictReader(f)
        for r in reader:

            data = {
            "title": r.get("title",""),
            "description": r.get("description",""),
            "date": r.get("date",""),
            "time": r.get("time",""),
            "priority": r.get("priority","Medium"),
            "alerts": int(r.get("alerts",1) or 1),
            }
            db.add_event(data)


def export_json(db: Database, filepath: Path | str):
    """Exports all events from the database to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(db.list_all(), f, ensure_ascii=False, indent=2)
         

def import_json(db: Database, filepath: Path | str):
    """Imports events from a JSON file and adds them to the database."""
    with open(filepath, encoding="utf-8") as f:
        arr = json.load(f)
    for r in arr:
        data = {
        "title": r.get("title",""),
        "description": r.get("description",""),
        "date": r.get("date",""),
        "time": r.get("time",""),
        "priority": r.get("priority","Medium"),
        "alerts": int(r.get("alerts",1) or 1),
        }
        db.add_event(data)