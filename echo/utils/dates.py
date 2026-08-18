from __future__ import annotations
from datetime import datetime
from dateutil import tz

def now_tz(tz_name: str) -> datetime:
    tzinfo = tz.gettz(tz_name)
    return datetime.now(tzinfo)

def fmt_ts(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")


def calendar_staleness_message(cfg: dict, today=None) -> str | None:
    """Return a warning string when the config calendar has gone stale, else None.

    Generic check shared by every dashboard view: each calendar section
    (calendar.fomc_dates, calendar.earnings) is stale when its LATEST date is
    before `today`. Calendar-driven signals (FOMC Tilt, and PEAD when the live
    earnings fetch fails) silently read as "no signal" on a stale calendar,
    which looks identical to a genuinely quiet market — hence the loud banner.
    Unparseable entries are ignored here (the signal rules surface those).
    """
    from dateutil import parser as _parser

    if today is None:
        today = datetime.now().date()
    cal = (cfg or {}).get("calendar", {}) or {}

    def _latest(raw_dates):
        parsed = []
        for s in raw_dates:
            try:
                parsed.append(_parser.parse(str(s)).date())
            except (ValueError, OverflowError):
                continue
        return max(parsed) if parsed else None

    stale = []
    fomc_latest = _latest(cal.get("fomc_dates", []) or [])
    if fomc_latest is not None and fomc_latest < today:
        stale.append(f"calendar.fomc_dates (latest {fomc_latest.isoformat()}, "
                     f"{(today - fomc_latest).days}d ago — FOMC Tilt cannot fire)")
    earn_latest = _latest((cal.get("earnings", {}) or {}).values())
    if earn_latest is not None and earn_latest < today:
        stale.append(f"calendar.earnings (latest {earn_latest.isoformat()}, "
                     f"{(today - earn_latest).days}d ago — PEAD's offline fallback is dead)")
    if not stale:
        return None
    return ("Stale calendar in echo/config.yaml: " + "; ".join(stale) +
            ". Update the dated entries to re-arm the affected signals.")
