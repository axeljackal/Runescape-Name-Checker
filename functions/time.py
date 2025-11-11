from datetime import datetime

def get_time():
    """Return current time as formatted string (HH:MM:SS)."""
    return datetime.now().strftime("%H:%M:%S")
