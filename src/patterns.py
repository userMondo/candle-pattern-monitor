"""
Candlestick Pattern Detection

Analyzes closed candlesticks for common reversal patterns:
- Engulfing (Bullish & Bearish)
- Doji + Engulfing (high-probability reversal combo)
- Doji (indecision)
- Hammer / Hanging
- Shooting Star / Inverted Hammer
- Pinbar (Bullish & Bearish)
- Morning Star
- Evening Star

Each pattern detector returns a dict with:
  - name: Human-readable pattern name
  - direction: "bullish" or "bearish"
  - strength: 1-3 scale
  - description: Short explanation
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

# Support both relative and absolute imports for testing
try:
    from .binance_client import Candle
except ImportError:
    from binance_client import Candle


# ---------------------------------------------------------------------------
# Individual Pattern Detectors
# ---------------------------------------------------------------------------

def detect_engulfing(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect bullish or bearish engulfing pattern.

    Bullish Engulfing: Bearish candle followed by a larger bullish candle
    that completely engulfs the previous candle's body.
    Bearish Engulfing: Bullish candle followed by a larger bearish candle
    that completely engulfs the previous candle's body.

    Requires at least 2 candles.
    """
    if len(candles) < 2:
        return None

    c0 = candles[-2]  # Previous candle
    c1 = candles[-1]  # Current (latest) candle

    if c0.is_bullish and c1.is_bearish:
        # Bearish Engulfing
        if c1.body_size >= c0.body_size and c1.open >= c0.close and c1.close <= c0.open:
            return {
                "name": "Bearish Engulfing",
                "direction": "bearish",
                "strength": 2,
                "description": "Large bearish candle fully engulfs preceding bullish candle — potential bearish reversal.",
            }

    elif c0.is_bearish and c1.is_bullish:
        # Bullish Engulfing
        if c1.body_size >= c0.body_size and c1.open <= c0.close and c1.close >= c0.open:
            return {
                "name": "Bullish Engulfing",
                "direction": "bullish",
                "strength": 2,
                "description": "Large bullish candle fully engulfs preceding bearish candle — potential bullish reversal.",
            }

    return None


def detect_hammer(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Hammer (bullish) or Hanging (bearish) pattern.

    A Hammer has a small body at the top with a long lower wick (2x body).
    A Shooting Star / Inverted Hammer has a small body at the bottom
    with a long upper wick.

    In an uptrend, it's a Hanging (bearish reversal signal).
    In a downtrend, it's a Hammer (bullish reversal signal).
    """
    if len(candles) < 2:
        return None

    c1 = candles[-1]
    c0 = candles[-2]
    body = c1.body_size
    upper_wick = c1.wick_upper
    lower_wick = c1.wick_lower

    if body == 0:
        return None  # Skip dojis, handled separately

    # Hammer: long lower wick (>= 2x body), short upper wick
    if lower_wick >= 2 * body and upper_wick < body:
        trend = "downtrend" if c1.close < c0.close else "uptrend"
        if c0.is_bearish or trend == "downtrend":
            return {
                "name": "Hammer",
                "direction": "bullish",
                "strength": 2,
                "description": "Small body at top of candle with long lower wick (2x+) — potential bullish reversal at support.",
            }
        else:
            return {
                "name": "Hanging Man",
                "direction": "bearish",
                "strength": 2,
                "description": "Small body at top with long lower wick in uptrend — potential bearish reversal at resistance.",
            }

    return None


def detect_shooting_star(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Shooting Star / Inverted Hammer pattern.

    Small body at bottom with long upper wick (>= 2x body).
    In uptrend = Shooting Star (bearish reversal).
    In downtrend = Inverted Hammer (bullish reversal signal, less reliable).
    """
    if len(candles) < 2:
        return None

    c1 = candles[-1]
    c0 = candles[-2]
    body = c1.body_size
    upper_wick = c1.wick_upper
    lower_wick = c1.wick_lower

    if body == 0:
        return None

    # Shooting Star: long upper wick (>= 2x body), short lower wick
    if upper_wick >= 2 * body and lower_wick < body:
        if c0.is_bullish or c1.close > c0.close:
            return {
                "name": "Shooting Star",
                "direction": "bearish",
                "strength": 2,
                "description": "Small body at bottom with long upper wick (2x+) in uptrend — potential bearish reversal at resistance.",
            }
        else:
            return {
                "name": "Inverted Hammer",
                "direction": "bullish",
                "strength": 1,
                "description": "Small body at bottom with long upper wick in downtrend — potential bullish reversal signal (less reliable).",
            }

    return None


def detect_doji(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Doji pattern.

    Open and close are nearly equal — market indecision.
    Bullish/neutral if appearing after downtrend.
    Bearish/neutral if appearing after uptrend.
    """
    if len(candles) < 1:
        return None

    c1 = candles[-1]
    # Doji: body is very small relative to range (< 5% of total range)
    if c1.total_range == 0:
        return None

    body_ratio = c1.body_size / c1.total_range

    if body_ratio < 0.05:
        return {
            "name": "Doji",
            "direction": "neutral",
            "strength": 1,
            "description": "Open and close nearly equal — market indecision, potential reversal signal.",
        }

    return None


def detect_pinbar(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Pinbar (outside bar) pattern.

    A candle with a long wick and small body, where the body is
    at one extreme and the wick extends beyond the previous candle's range.

    Bullish Pinbar: Long lower wick, body at/near top, wick penetrates below
                  previous candle's low.
    Bearish Pinbar: Long upper wick, body at/near bottom, wick penetrates above
                  previous candle's high.
    """
    if len(candles) < 2:
        return None

    c0 = candles[-2]
    c1 = candles[-1]
    body = c1.body_size

    if c1.total_range == 0:
        return None

    # Body should be small (less than 1/3 of total range)
    if body / c1.total_range > 0.33:
        return None

    upper_wick = c1.wick_upper
    lower_wick = c1.wick_lower

    # Bullish Pinbar: long lower wick penetrating below previous low
    if lower_wick > upper_wick and lower_wick >= body * 2:
        if c1.low < c0.low:
            return {
                "name": "Bullish Pinbar",
                "direction": "bullish",
                "strength": 3,
                "description": "Long lower wick penetrating below previous low with small body at top — strong bullish reversal signal.",
            }

    # Bearish Pinbar: long upper wick penetrating above previous high
    if upper_wick > lower_wick and upper_wick >= body * 2:
        if c1.high > c0.high:
            return {
                "name": "Bearish Pinbar",
                "direction": "bearish",
                "strength": 3,
                "description": "Long upper wick penetrating above previous high with small body at bottom — strong bearish reversal signal.",
            }

    return None


def detect_morning_star(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Morning Star pattern (bullish reversal, 3 candles).

    1. Large bearish candle
    2. Small candle (or doji) that gaps down
    3. Large bullish candle that closes above midpoint of candle 1
    """
    if len(candles) < 3:
        return None

    c0 = candles[-3]  # First: large bearish
    c1 = candles[-2]  # Second: small, gaps down
    c2 = candles[-1]  # Third: large bullish, closes mid-c0

    # C1: small body (continuation of downtrend gap)
    c1_body_ratio = c1.body_size / c1.total_range if c1.total_range > 0 else 0
    if c1_body_ratio >= 0.3:
        return None

    # C0: large bearish
    if not c0.is_bearish:
        return None

    # C2: large bullish, closes above midpoint of c0
    midpoint_c0 = (c0.open + c0.close) / 2
    if c2.close > midpoint_c0 and c2.body_size > c1.body_size:
        return {
            "name": "Morning Star",
            "direction": "bullish",
            "strength": 3,
            "description": "3-candle bullish reversal: large red, small red/gap down, large green closing above midpoint of first candle.",
        }

    return None


def detect_evening_star(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Evening Star pattern (bearish reversal, 3 candles).

    1. Large bullish candle
    2. Small candle (or doji) that gaps up
    3. Large bearish candle that closes below midpoint of candle 1
    """
    if len(candles) < 3:
        return None

    c0 = candles[-3]  # First: large bullish
    c1 = candles[-2]  # Second: small, gaps up
    c2 = candles[-1]  # Third: large bearish, closes below midpoint of c0

    # C1: small body
    c1_body_ratio = c1.body_size / c1.total_range if c1.total_range > 0 else 0
    if c1_body_ratio >= 0.3:
        return None

    # C0: large bullish
    if not c0.is_bullish:
        return None

    # C2: large bearish, closes below midpoint of c0
    midpoint_c0 = (c0.open + c0.close) / 2
    if c2.close < midpoint_c0 and c2.body_size > c1.body_size:
        return {
            "name": "Evening Star",
            "direction": "bearish",
            "strength": 3,
            "description": "3-candle bearish reversal: large green, small green/gap up, large red closing below midpoint of first candle.",
        }

    return None


def detect_doji_engulfing(candles: List[Candle]) -> Optional[Dict]:
    """
    Detect Doji + Engulfing pattern.

    A Doji followed by or part of an Engulfing pattern — high-probability
    reversal signal combining indecision (Doji) with momentum (Engulfing).

    Checks for:
    1. Doji candle (c0) followed by Bullish Engulfing (c1): Strong trend reversal
    2. Doji candle (c0) followed by Bearish Engulfing (c1): Strong trend reversal

    Requires at least 2 candles.
    """
    if len(candles) < 2:
        return None

    c0 = candles[-2]
    c1 = candles[-1]

    # Check if c0 is a doji (small body relative to range)
    # A doji has open ~= close (body is tiny relative to total range)
    c0_is_doji = False
    if c0.total_range > 0:
        c0_body_ratio = c0.body_size / c0.total_range
        c0_is_doji = c0_body_ratio < 0.1  # < 10% of range

    if not c0_is_doji:
        return None

    # Determine the doji's trend context:
    # If c0 is a perfect doji (open==close), use the candle before it (c_prev)
    # If c0 has a tiny body, use its own direction
    c_prev = candles[-3] if len(candles) >= 3 else None

    # Determine trend direction before the doji
    if c0.body_size > 0:
        # Near-doji with small body: use its own direction
        c0_is_bearish = c0.is_bearish
        c0_is_bullish = c0.is_bullish
    elif c_prev is not None:
        # Perfect doji: infer direction from preceding candle
        c0_is_bearish = c_prev.is_bearish
        c0_is_bullish = c_prev.is_bullish
    else:
        # Perfect doji with no preceding candle: use close vs open of doji range
        # Fall back to checking if close is at top/bottom of the doji range
        if abs(c0.close - c0.high) < abs(c0.close - c0.low):
            c0_is_bearish = True
            c0_is_bullish = False
        else:
            c0_is_bearish = False
            c0_is_bullish = True

    # Check if c1 is an engulfing candle that breaks away from the doji
    # C1 should be a strong directional candle with body much larger than doji body
    if c0_is_bearish and c1.is_bullish:
        # Doji after downtrend, then bullish engulfing
        # C1 should fully engulf the doji's range (or at minimum gap up significantly)
        if c1.close > c0.open and c1.body_size > 0:
            return {
                "name": "Doji + Bullish Engulfing",
                "direction": "bullish",
                "strength": 3,
                "description": "Doji after downtrend followed by strong bullish engulfing — high-probability bullish reversal.",
            }

    elif c0_is_bullish and c1.is_bearish:
        # Doji after uptrend, then bearish engulfing
        if c1.close < c0.open and c1.body_size > 0:
            return {
                "name": "Doji + Bearish Engulfing",
                "direction": "bearish",
                "strength": 3,
                "description": "Doji after uptrend followed by strong bearish engulfing — high-probability bearish reversal.",
            }

    return None


def detect_patterns(
    candles: List[Candle],
    focus: Optional[List[str]] = None,
) -> List[Dict]:
    """
    Run pattern detectors against a list of candles.

    Returns the LATEST (most recent) candle's patterns.
    Each detector examines the most recent closed candle(s).

    Args:
        candles: List of Candle objects (oldest first).
        focus: Optional list of pattern category names to limit detection.
               If None, runs all detectors.
               Categories: "engulfing", "doji", "pinbar", "hammer", 
               "shooting_star", "morning_star", "evening_star".

    Returns:
        List of detected pattern dicts. Each dict has:
            - name: Pattern name
            - direction: "bullish", "bearish", or "neutral"
            - strength: 1-3
            - description: Human-readable description
    """
    if len(candles) < 2:
        return []

    all_detectors = [
        ("doji", "Doji", detect_doji),
        ("doji", "Doji + Engulfing", detect_doji_engulfing),
        ("pinbar", "Pinbar", detect_pinbar),
        ("hammer", "Hammer", detect_hammer),
        ("shooting_star", "Shooting Star", detect_shooting_star),
        ("engulfing", "Engulfing", detect_engulfing),
        ("morning_star", "Morning Star", detect_morning_star),
        ("evening_star", "Evening Star", detect_evening_star),
    ]

    detected = []
    for focus_cat, pattern_name, detector_fn in all_detectors:
        if focus and focus_cat not in focus:
            continue
        try:
            result = detector_fn(candles)
            if result:
                detected.append(result)
        except Exception as e:
            # Don't let one detector's bug kill the whole check
            print(f"[PatternDetector] Error in {pattern_name}: {e}")

    return detected


def format_pattern_alert(
    symbol: str,
    interval: str,
    patterns: List[Dict],
    candle: Candle,
    timestamp: str = "",
) -> str:
    """
    Format detected patterns into a human-readable Telegram alert string.
    """
    if not patterns:
        return ""

    lines = [
        f"🕯️ *Candle Pattern Alert*",
        f"",
        f"*Symbol:* `{symbol}`",
        f"*Timeframe:* `{interval}`",
        f"*Close:* `{candle.close:.2f}`",
        f"*Open:* `{candle.open:.2f}`",
        f"*High:* `{candle.high:.2f}`",
        f"*Low:* `{candle.low:.2f}`",
    ]

    if timestamp:
        lines.append(f"*Time:* `{timestamp}`")

    lines.append("")

    for p in patterns:
        lines.append(
            f"*Pattern:* `{p['name']}` ({p['direction'].upper()}, "
            f"strength: {p['strength']}/3)\n{p['description']}"
        )

    return "\n".join(lines)
