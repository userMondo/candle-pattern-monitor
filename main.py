"""
Entry point for the Candle Pattern Monitor.

Fetches candle data from Binance, detects patterns, and sends
Telegram alerts when patterns are found.

Usage:
    python main.py --symbols BTCUSDT,ETHUSDT --interval 4h
    python main.py  # Uses default symbols and interval from env
"""

import argparse
import os
import sys
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional

# Add src to path for direct execution
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from binance_client import BinanceClient, Candle
from telegram_bot import TelegramBot
from patterns import detect_patterns, format_pattern_alert, format_price_report


DEFAULT_SYMBOLS = "BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT"
DEFAULT_INTERVAL = os.getenv("INTERVAL", "15m")  # Primary: 15m, also run 1h and 4h
DEFAULT_LIMIT = 50

# Default focus: monitor ALL pattern types (no filtering)
DEFAULT_FOCUS = None  # None means detect all patterns


def parse_watchlist(symbols_env: str) -> List[str]:
    """Parse comma-separated watchlist into list of symbol strings."""
    if not symbols_env:
        return []
    return [s.strip().upper() for s in symbols_env.split(",") if s.strip()]


def check_symbol(
    client: BinanceClient,
    bot: Optional[TelegramBot],
    symbol: str,
    interval: str,
    limit: int = DEFAULT_LIMIT,
    focus: Optional[List[str]] = None,
) -> Dict:
    """
    Fetch candles for a symbol, detect patterns, send alert if found.

    Returns a summary dict of what was found.
    """
    result = {
        "symbol": symbol,
        "interval": interval,
        "patterns_found": [],
        "alert_sent": False,
        "error": None,
    }

    try:
        candles = client.get_klines(symbol, interval, limit=limit)
        if len(candles) < 3:
            result["error"] = f"Not enough candles ({len(candles)}) for pattern detection"
            return result

        # CRITICAL: Filter to only fully-closed candles.
        # The last candle in Binance's response may still be forming (unclosed).
        closed_candles = [c for c in candles if c.is_closed]
        if len(closed_candles) < 3:
            result["error"] = f"Not enough closed candles ({len(closed_candles)}) for pattern detection"
            return result

        # Use only closed candles for pattern detection
        candles = closed_candles
        latest_candle = candles[-1]
        patterns = detect_patterns(candles, focus=focus)

        if patterns and bot is not None:
            ts_utc = datetime.fromtimestamp(latest_candle.close_time / 1000, tz=timezone.utc)
            ts_local = ts_utc + timedelta(hours=7)  # UTC+7
            timestamp_str = ts_local.strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")

            alert_text = format_pattern_alert(
                symbol=symbol,
                interval=interval,
                patterns=patterns,
                candle=latest_candle,
                timestamp=timestamp_str,
            )

            sent = bot.send_message(alert_text, parse_mode="Markdown")
            result["alert_sent"] = sent
            result["patterns_found"] = [p["name"] for p in patterns]
        elif patterns and bot is None:
            # Patterns found but no bot configured
            ts_utc = datetime.fromtimestamp(latest_candle.close_time / 1000, tz=timezone.utc)
            ts_local = ts_utc + timedelta(hours=7)  # UTC+7
            timestamp_str = ts_local.strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")
            alert_text = format_pattern_alert(
                symbol=symbol,
                interval=interval,
                patterns=patterns,
                candle=latest_candle,
                timestamp=timestamp_str,
            )
            print(f"  📋 Patterns found (no Telegram): {alert_text[:100]}...")
            result["patterns_found"] = [p["name"] for p in patterns]
        else:
            result["patterns_found"] = []

    except Exception as e:
        result["error"] = str(e)

    return result


def run_price_report(binance_client: BinanceClient, telegram_bot: Optional[TelegramBot], symbols: List[str]) -> int:
    """Fetch 24h price tickers for all symbols and send as a Telegram report.

    This is the hourly price report mode — always runs and sends regardless
    of whether any pattern is detected.
    """
    from datetime import datetime, timezone, timedelta
    ts_utc = datetime.now(timezone.utc)
    ts_local = ts_utc + timedelta(hours=7)
    timestamp_str = ts_local.strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")

    tickers = []
    for symbol in symbols:
        try:
            ticker = binance_client.get_price_ticker(symbol)
            tickers.append(ticker)
            print(f"  ✅ {symbol}: ${ticker['price']:.4f} ({ticker['price_change_pct']:+.2f}%)")
        except Exception as e:
            print(f"  ❌ {symbol}: {e}")

    if not tickers:
        print("No tickers fetched. Exiting.")
        return 1

    report = format_price_report(tickers, timestamp=timestamp_str)
    print(f"\n{report}")

    if telegram_bot is not None:
        sent = telegram_bot.send_message(report, parse_mode="Markdown")
        print(f"\n📨 Price report sent: {sent}")
    else:
        print("\n⚠️  No Telegram bot configured — price report not sent.")

    return 0


def main():
    parser = argparse.ArgumentParser(description="Candle Pattern Monitor")
    parser.add_argument(
        "--symbols",
        default=os.getenv("WATCHLIST_SYMBOLS", DEFAULT_SYMBOLS),
        help="Comma-separated trading pairs (default: BTCUSDT,ETHUSDT,SOLUSDT)",
    )
    parser.add_argument(
        "--interval",
        default=os.getenv("INTERVAL", DEFAULT_INTERVAL),
        help="Kline interval: 15m, 1h, or 4h (default: 4h)",
    )
    parser.add_argument(
        "--focus",
        default=os.getenv("PATTERN_FOCUS", ""),
        help="Pattern categories to focus on (comma-separated). "
             "Empty = detect ALL patterns. Options: "
             "engulfing, doji, pinbar, hammer, shooting_star, morning_star, evening_star",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.getenv("CANDLE_LIMIT", str(DEFAULT_LIMIT))),
        help="Number of candles to fetch per symbol (default: 50)",
    )
    parser.add_argument(
        "--price-report",
        action="store_true",
        default=os.getenv("PRICE_REPORT", "").lower() in ("true", "1", "yes"),
        help="Send hourly price report for all watched symbols (instead of/in addition to pattern alerts)",
    )

    args = parser.parse_args()
    symbols = parse_watchlist(args.symbols)
    focus = [f.strip().lower() for f in args.focus.split(",") if f.strip()] if args.focus else None

    if not symbols:
        print("No symbols provided. Exiting.")
        sys.exit(1)

    print(f"Monitoring {len(symbols)} symbols: {symbols}")
    print(f"Interval: {args.interval}")
    if focus:
        print(f"Pattern focus: {focus}")
    if args.price_report:
        print("Mode: Price Report (hourly ticker summary)")

    # Initialize clients
    binance_client = BinanceClient()
    try:
        telegram_bot = TelegramBot()
    except ValueError as e:
        print(f"⚠️  Telegram config issue: {e}")
        print("   Alerts won't be sent (pattern detection still runs).")
        telegram_bot = None

    # Price report mode — send hourly ticker for all symbols
    if args.price_report:
        return run_price_report(binance_client, telegram_bot, symbols)

    results = []
    for symbol in symbols:
        print(f"\nChecking {symbol}...")
        result = check_symbol(binance_client, telegram_bot, symbol, args.interval, args.limit, focus)
        results.append(result)

        if result["patterns_found"]:
            print(f"  ✅ Patterns found: {result['patterns_found']}")
            print(f"  📨 Alert sent: {result['alert_sent']}")
        elif result["error"]:
            print(f"  ❌ Error: {result['error']}")
        else:
            print(f"  No patterns detected.")

    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    total_patterns = sum(len(r["patterns_found"]) for r in results)
    total_alerts = sum(1 for r in results if r["alert_sent"])
    errors = [r for r in results if r["error"]]

    print(f"Symbols checked: {len(results)}")
    print(f"Patterns detected: {total_patterns}")
    print(f"Alerts sent: {total_alerts}")
    if errors:
        print(f"Errors: {len(errors)}")
        for e in errors:
            print(f"  - {e['symbol']}: {e['error']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
