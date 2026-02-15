from datetime import datetime, timedelta
# Standard date and time display/parsing formats
TIME_FORMAT = "%H:%M"
DATE_FORMAT = "%Y-%m-%d"
DT_FORMAT   = "%Y-%m-%d %H:%M"


def parse_time(hhmm: str) -> datetime:
    """Converts 'HH:MM' string into a datetime object."""
    return datetime.strptime(hhmm, TIME_FORMAT)
    

def combine(date_str: str, time_str: str) -> datetime:
    """Combines a date and a time string into a single datetime object."""
    return datetime.strptime(f"{date_str} {time_str}", DT_FORMAT)


def human_countdown(delta: timedelta) -> str:
    """Receives a timedelta and converts it into a human-readable string."""
    total_seconds = int(delta.total_seconds()) 
    if total_seconds <= 0 :
        return "Event is ongoing or has passed."
    
    
    minutes = (total_seconds // 60) % 60 
    hours = (total_seconds // 3600) % 24 
    days = total_seconds // 86400 
    parts = [] 


    if days:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes !=1 else ''}")
    return " ".join(parts)

def now_iso_minute(hours: int) -> str:
    """Returns the current date and time formatted as a string, with an optional hour offset."""
    return (datetime.now() + timedelta(hours=hours)).strftime(DT_FORMAT)

