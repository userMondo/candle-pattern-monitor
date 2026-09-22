"""
Tests for candlestick pattern detection.

These tests use synthetic candle data to verify pattern detection logic
without requiring live Binance API calls.
"""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from binance_client import Candle
from patterns import (
    detect_patterns,
    detect_engulfing,
    detect_hammer,
    detect_shooting_star,
    detect_doji,
    detect_doji_engulfing,
    detect_pinbar,
    detect_morning_star,
    detect_evening_star,
    format_pattern_alert,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_candle(open_price, high, low, close, volume=1.0, open_time=0, close_time=60000):
    """
    Create a Candle instance with sensible defaults.

    Constraints: high >= max(open, close) and low <= min(open, close).
    """
    return Candle(
        open_time=open_time,
        open=open_price,
        high=max(high, open_price, close),
        low=min(low, open_price, close),
        close=close,
        volume=volume,
        close_time=close_time,
    )


# ---------------------------------------------------------------------------
# Engulfing Tests
# ---------------------------------------------------------------------------

class TestEngulfing:
    def test_bullish_engulfing(self):
        """Bullish engulfing: bearish then larger bullish."""
        c0 = make_candle(100, 100, 95, 96)   # bearish
        c1 = make_candle(95, 105, 94, 104)  # bullish, engulfs c0
        result = detect_engulfing([c0, c1])
        assert result is not None
        assert result["name"] == "Bullish Engulfing"
        assert result["direction"] == "bullish"

    def test_bearish_engulfing(self):
        """Bearish engulfing: bullish then larger bearish."""
        c0 = make_candle(95, 105, 94, 104)   # bullish
        c1 = make_candle(104, 110, 90, 93)  # bearish, engulfs c0
        result = detect_engulfing([c0, c1])
        assert result is not None
        assert result["name"] == "Bearish Engulfing"
        assert result["direction"] == "bearish"

    def test_no_engulfing(self):
        """No engulfing when body doesn't fully contain previous."""
        c0 = make_candle(100, 100, 95, 96)  # bearish
        c1 = make_candle(96, 100, 95, 99)   # small bullish, doesn't engulf
        result = detect_engulfing([c0, c1])
        assert result is None

    def test_insufficient_candles(self):
        result = detect_engulfing([make_candle(100, 100, 95, 96, open_time=0)])
        assert result is None


# ---------------------------------------------------------------------------
# Doji Tests
# ---------------------------------------------------------------------------

class TestDoji:
    def test_perfect_doji(self):
        """Open == close with small body relative to range."""
        c0 = make_candle(100, 108, 92, 100)  # perfect doji
        result = detect_doji([c0])
        assert result is not None
        assert result["name"] == "Doji"
        assert result["direction"] == "neutral"

    def test_not_doji(self):
        """Large body = not a doji."""
        c0 = make_candle(100, 108, 95, 106)
        result = detect_doji([c0])
        assert result is None


# ---------------------------------------------------------------------------
# Hammer Tests
# ---------------------------------------------------------------------------

class TestHammer:
    def test_bullish_hammer(self):
        """Hammer: long lower wick, small body at top, after downtrend."""
        c0 = make_candle(100, 100, 95, 96)   # small bearish
        c1 = make_candle(96, 99, 86, 98)     # long lower wick, small body at top
        result = detect_hammer([c0, c1])
        assert result is not None
        assert result["name"] == "Hammer"
        assert result["direction"] == "bullish"

    def test_hanging_man(self):
        """Hanging Man: hammer pattern in uptrend."""
        c0 = make_candle(90, 100, 89, 99)    # bullish (close=99 > open=90)
        c1 = make_candle(99.2, 99.3, 88, 99.1)  # tiny upper wick, long lower wick
        result = detect_hammer([c0, c1])
        assert result is not None
        # In uptrend context, results in Hanging Man or Hammer
        assert result["direction"] in ("bullish", "bearish")

    def test_no_hammer(self):
        """No long lower wick = no hammer."""
        c0 = make_candle(100, 100, 95, 96)
        c1 = make_candle(96, 103, 94, 101)  # short lower wick
        result = detect_hammer([c0, c1])
        assert result is None


# ---------------------------------------------------------------------------
# Shooting Star Tests
# ---------------------------------------------------------------------------

class TestShootingStar:
    def test_bearish_shooting_star(self):
        """Shooting Star: long upper wick, small body at bottom."""
        c0 = make_candle(96, 102, 95, 100)   # bullish
        c1 = make_candle(100, 108, 96, 97)   # long upper wick, small body
        result = detect_shooting_star([c0, c1])
        assert result is not None
        assert result["name"] == "Shooting Star"
        assert result["direction"] == "bearish"

    def test_no_shooting_star(self):
        """No long upper wick = no shooting star."""
        c0 = make_candle(96, 102, 95, 100)
        c1 = make_candle(100, 103, 96, 101)  # short wicks
        result = detect_shooting_star([c0, c1])
        assert result is None


# ---------------------------------------------------------------------------
# Pinbar Tests
# ---------------------------------------------------------------------------

class TestPinbar:
    def test_bullish_pinbar(self):
        """Bullish Pinbar: long lower wick below previous low."""
        c0 = make_candle(100, 100, 98, 99)
        c1 = make_candle(99, 100, 89, 99.5)  # long lower wick, body at top
        result = detect_pinbar([c0, c1])
        assert result is not None
        assert result["name"] == "Bullish Pinbar"
        assert result["direction"] == "bullish"

    def test_bearish_pinbar(self):
        """Bearish Pinbar: long upper wick above previous high."""
        c0 = make_candle(100, 102, 99, 101)
        c1 = make_candle(101, 110, 98, 100)  # long upper wick, body at bottom
        result = detect_pinbar([c0, c1])
        assert result is not None
        assert result["name"] == "Bearish Pinbar"
        assert result["direction"] == "bearish"

    def test_no_pinbar(self):
        """Body too large relative to range = no pinbar."""
        c0 = make_candle(100, 100, 98, 99)
        c1 = make_candle(99, 110, 90, 108)  # large body
        result = detect_pinbar([c0, c1])
        assert result is None


# ---------------------------------------------------------------------------
# Morning Star / Evening Star Tests
# ---------------------------------------------------------------------------

class TestMorningStar:
    def test_morning_star(self):
        """Morning Star: bullish reversal over 3 candles."""
        c0 = make_candle(100, 100, 95, 96)        # large bearish
        c1 = make_candle(96, 97, 91, 96.5)        # small body, gaps down
        c2 = make_candle(96.5, 105, 92, 102)      # large bullish
        result = detect_morning_star([c0, c1, c2])
        assert result is not None
        assert result["name"] == "Morning Star"
        assert result["direction"] == "bullish"


class TestEveningStar:
    def test_evening_star(self):
        """Evening Star: bearish reversal over 3 candles."""
        c0 = make_candle(95, 100, 94, 99)         # large bullish
        c1 = make_candle(99, 101, 96, 98.5)       # small body, gaps up
        c2 = make_candle(98.5, 101, 92, 95)       # large bearish
        result = detect_evening_star([c0, c1, c2])
        assert result is not None
        assert result["name"] == "Evening Star"
        assert result["direction"] == "bearish"


# ---------------------------------------------------------------------------
# Integration: detect_patterns
# ---------------------------------------------------------------------------

class TestDetectPatterns:
    def test_returns_list(self):
        """detect_patterns returns a list."""
        candles = [make_candle(100, 100, 95, 96), make_candle(95, 105, 94, 104)]
        result = detect_patterns(candles)
        assert isinstance(result, list)

    def test_detects_multiple_patterns(self):
        """Multiple patterns can be detected simultaneously."""
        c0 = make_candle(100, 100, 95, 96)
        c1 = make_candle(95, 105, 94, 104)  # bullish engulfing
        result = detect_patterns([c0, c1])
        assert len(result) > 0

    def test_empty_list_on_insufficient_candles(self):
        result = detect_patterns([make_candle(100, 100, 95, 96)])
        assert result == []


# ---------------------------------------------------------------------------
# Format Alert Tests
# ---------------------------------------------------------------------------

class TestFormatAlert:
    def test_format_with_patterns(self):
        c1 = make_candle(95, 105, 94, 104)
        patterns = [
            {"name": "Bullish Engulfing", "direction": "bullish", "strength": 2, "description": "Test desc"},
        ]
        alert = format_pattern_alert("BTCUSDT", "4h", patterns, c1)
        assert "BTCUSDT" in alert
        assert "4h" in alert
        assert "Bullish Engulfing" in alert
        assert "104.00" in alert

    def test_empty_patterns_returns_empty(self):
        c1 = make_candle(95, 105, 94, 104)
        alert = format_pattern_alert("BTCUSDT", "4h", [], c1)
        assert alert == ""


# ---------------------------------------------------------------------------
# Doji + Engulfing Tests
# ---------------------------------------------------------------------------

class TestDojiEngulfing:
    def test_bullish_doji_engulfing(self):
        """Doji after downtrend followed by bullish engulfing candle."""
        c0 = make_candle(100, 100, 92, 100)  # doji (open==close)
        c1 = make_candle(99, 110, 92, 108)   # strong bullish, body >> doji body
        result = detect_doji_engulfing([c0, c1])
        assert result is not None
        assert result["name"] == "Doji + Bullish Engulfing"
        assert result["direction"] == "bullish"
        assert result["strength"] == 3

    def test_bearish_doji_engulfing(self):
        """Doji after uptrend followed by bearish engulfing candle."""
        c_prev = make_candle(88, 98, 87, 96)  # bullish uptrend
        c0 = make_candle(96, 98, 94, 96)      # near-doji (small body)
        c1 = make_candle(96, 98, 80, 82)     # strong bearish
        result = detect_doji_engulfing([c_prev, c0, c1])
        assert result is not None
        assert result["name"] == "Doji + Bearish Engulfing"
        assert result["direction"] == "bearish"

    def test_no_doji_engulfing_without_doji(self):
        """No Doji+Engulfing if c0 is not a doji."""
        c0 = make_candle(100, 110, 90, 108)  # large body, not a doji
        c1 = make_candle(108, 100, 90, 92)   # bearish engulfing
        result = detect_doji_engulfing([c0, c1])
        assert result is None

    def test_no_doji_engulfing_insufficient_candles(self):
        result = detect_doji_engulfing([make_candle(100, 100, 92, 100)])
        assert result is None


# ---------------------------------------------------------------------------
# Pattern Focus Tests
# ---------------------------------------------------------------------------

class TestPatternFocus:
    def test_focus_engulfing_only(self):
        """Focus on engulfing only — should not detect doji."""
        c0 = make_candle(100, 100, 92, 100)  # doji
        c1 = make_candle(99, 99, 88, 99)    # doji
        doji_only = make_candle(100, 108, 92, 100)  # pure doji
        result = detect_patterns([doji_only], focus=["engulfing"])
        # With focus on engulfing only, doji should not be detected
        for p in result:
            assert "Doji" not in p["name"], "Doji should not be in engulfing focus"

    def test_focus_all(self):
        """With no focus, all patterns should be checked."""
        c0 = make_candle(100, 100, 95, 96)
        c1 = make_candle(95, 105, 94, 104)
        result = detect_patterns([c0, c1], focus=None)
        assert isinstance(result, list)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Closed Candle Tests
# ---------------------------------------------------------------------------

class TestClosedCandle:
    def test_candle_is_closed(self):
        """Candle with close_time in the past is marked as closed."""
        import time
        past_time = int(time.time() * 1000) - 60000  # 1 minute ago
        c = make_candle(100, 105, 95, 102, close_time=past_time)
        assert c.is_closed is True

    def test_candle_not_closed(self):
        """Candle with close_time in the future is marked as not closed."""
        import time
        future_time = int(time.time() * 1000) + 600000  # 10 minutes in future
        c = make_candle(100, 105, 95, 102, close_time=future_time)
        assert c.is_closed is False
