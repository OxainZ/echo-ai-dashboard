"""Offline tests for the calendar-driven signals and the staleness guard.

Run with:  python -m unittest discover tests
No network and no yfinance import needed — providers are stubbed.
"""
from __future__ import annotations
import os
import sys
import unittest
from datetime import date, datetime

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from echo.rules.fomc_tilt import FOMCTilt          # noqa: E402
from echo.rules.pead import PEAD                   # noqa: E402
from echo.utils.dates import calendar_staleness_message  # noqa: E402

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "echo", "config.yaml")


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


class StubProvider:
    def __init__(self, dates=None, raise_on_call=False):
        self._dates = dates or []
        self._raise = raise_on_call

    def earnings_dates(self, ticker):
        if self._raise:
            raise RuntimeError("network down")
        return sorted(self._dates)


def ctx(cfg, now, provider=None, slots=None):
    return {
        "now": now,
        "config": cfg,
        "provider": provider,
        "slots": slots or {"momentum": "TSLA", "wildcard": "AMZN"},
    }


class TestConfigCalendar(unittest.TestCase):
    def test_config_parses_and_fomc_dates_are_valid(self):
        cfg = load_config()
        dates = [date.fromisoformat(d) for d in cfg["calendar"]["fomc_dates"]]
        self.assertEqual(len(dates), 11)  # 3 remaining 2026 + 8 announced 2027
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(dates[0], date(2026, 9, 16))
        self.assertEqual(dates[-1], date(2027, 12, 8))
        # No stale (pre-2026-08) dates left in the list.
        self.assertTrue(all(d >= date(2026, 8, 18) for d in dates))


class TestFOMCTilt(unittest.TestCase):
    def test_fires_day_before_decision(self):
        cfg = load_config()
        sig = FOMCTilt().run(ctx(cfg, datetime(2026, 9, 15, 10, 0)))
        self.assertEqual(sig.score, 80.0)
        self.assertEqual(sig.severity, "yellow")

    def test_fires_before_june_2027_decision(self):
        # 2027 meeting is Jun 8-9 -> decision day Jun 9 -> tilt on Jun 8.
        cfg = load_config()
        sig = FOMCTilt().run(ctx(cfg, datetime(2027, 6, 8, 10, 0)))
        self.assertEqual(sig.score, 80.0)

    def test_quiet_on_other_days(self):
        cfg = load_config()
        for day in (datetime(2026, 9, 14), datetime(2026, 9, 16), datetime(2026, 8, 18)):
            sig = FOMCTilt().run(ctx(cfg, day))
            self.assertEqual(sig.score, 0.0)
            self.assertEqual(sig.severity, "green")


class TestPEAD(unittest.TestCase):
    def test_live_post_earnings_drift(self):
        cfg = load_config()
        provider = StubProvider([date(2026, 8, 10), date(2026, 10, 21)])
        sig = PEAD("momentum").run(ctx(cfg, datetime(2026, 8, 18), provider))
        self.assertGreaterEqual(sig.score, 30.0)
        self.assertIn("drift day 8", sig.detail)
        self.assertIn("live", sig.detail)

    def test_live_pre_earnings_uses_next_date(self):
        cfg = load_config()
        provider = StubProvider([date(2026, 4, 22), date(2026, 10, 21)])
        sig = PEAD("momentum").run(ctx(cfg, datetime(2026, 8, 18), provider))
        self.assertEqual(sig.score, 60.0)  # TSLA has a positive whisper gap in config
        self.assertIn("2026-10-21", sig.detail)

    def test_fallback_stale_guard(self):
        # Live fetch fails and the config fallback (2025) is stale ->
        # explicit yellow "unavailable" signal, not a silent green zero.
        cfg = load_config()
        provider = StubProvider(raise_on_call=True)
        sig = PEAD("momentum").run(ctx(cfg, datetime(2026, 8, 18), provider))
        self.assertEqual(sig.score, 0)
        self.assertEqual(sig.severity, "yellow")
        self.assertIn("stale", sig.detail)

    def test_fallback_fresh_config_date_still_works(self):
        cfg = load_config()
        cfg["calendar"]["earnings"]["TSLA"] = "2026-10-21"
        provider = StubProvider([])  # live fetch empty
        sig = PEAD("momentum").run(ctx(cfg, datetime(2026, 10, 22), provider))
        self.assertIn("drift day 1", sig.detail)
        self.assertIn("config fallback", sig.detail)

    def test_no_date_anywhere(self):
        cfg = load_config()
        cfg["calendar"]["earnings"] = {}
        sig = PEAD("momentum").run(ctx(cfg, datetime(2026, 8, 18), StubProvider([])))
        self.assertEqual(sig.score, 0)
        self.assertEqual(sig.severity, "green")


class TestStalenessMessage(unittest.TestCase):
    def test_current_config_flags_only_earnings_fallback(self):
        cfg = load_config()
        msg = calendar_staleness_message(cfg, today=date(2026, 8, 18))
        self.assertIsNotNone(msg)
        self.assertIn("calendar.earnings", msg)
        self.assertNotIn("calendar.fomc_dates", msg)

    def test_all_fresh_is_quiet(self):
        cfg = {"calendar": {"fomc_dates": ["2026-09-16"],
                            "earnings": {"TSLA": "2026-10-21"}}}
        self.assertIsNone(calendar_staleness_message(cfg, today=date(2026, 8, 18)))

    def test_stale_fomc_is_named_with_age(self):
        cfg = {"calendar": {"fomc_dates": ["2025-09-17"], "earnings": {}}}
        msg = calendar_staleness_message(cfg, today=date(2026, 8, 18))
        self.assertIn("calendar.fomc_dates", msg)
        self.assertIn("2025-09-17", msg)
        self.assertIn("335d ago", msg)

    def test_empty_calendar_is_quiet(self):
        self.assertIsNone(calendar_staleness_message({}, today=date(2026, 8, 18)))
        self.assertIsNone(calendar_staleness_message({"calendar": {}}, today=date(2026, 8, 18)))

    def test_unparseable_entries_are_skipped(self):
        cfg = {"calendar": {"fomc_dates": ["not-a-date", "2027-12-08"], "earnings": {}}}
        self.assertIsNone(calendar_staleness_message(cfg, today=date(2026, 8, 18)))


if __name__ == "__main__":
    unittest.main()
