from __future__ import annotations
from datetime import datetime
from dateutil import tz

def now_tz(tz_name: str) -> datetime:
    tzinfo = tz.gettz(tz_name)
    return datetime.now(tzinfo)

def fmt_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")
