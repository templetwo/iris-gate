import os, datetime
from zoneinfo import ZoneInfo

def now_iso():
    """Get current time in IRIS canonical timezone (US Northeast)."""
    tz = os.environ.get("IRIS_TZ", "America/New_York")
    return datetime.datetime.now(ZoneInfo(tz)).isoformat()

def now_timestamp():
    """Get simple timestamp for filenames (YYYYMMDD_HHMMSS)."""
    tz = os.environ.get("IRIS_TZ", "America/New_York")
    return datetime.datetime.now(ZoneInfo(tz)).strftime("%Y%m%d_%H%M%S")
