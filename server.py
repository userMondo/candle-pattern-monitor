#!/usr/bin/env python3
"""
Always-on candle monitor with hourly price reports.

Unlike GitHub Actions (which spins up a fresh VM every 15 min), this script
runs continuously as a single persistent process — like a VPS daemon.

It monitors:
  - Pattern alerts: checks every interval for reversal patterns
  - Price reports: sends 24h summary every hour

Usage:
    python server.py [--symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT]
                     [--interval 15m]
                     [--price-report-interval 1h]

Requirements:
    pip install requests python-dotenv

The script uses Binance public API + Telegram bot.
No external dependencies beyond `requests`.

Press Ctrl+C to stop cleanly.
"""
import argparse
import os
import sys
import time
import traceback
from datetime import datetime, timezone, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from binance_client import BinanceClient
from telegram_bot import TelegramBot
from patterns import detect_patterns, format_pattern_alert, format_price_report


def load_env():
    """Load .env file if present."""
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path)
        except ImportError:
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        v = v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v


def utc_plus_7():
    """Return current UTC+7 aware datetime."""
    return datetime.now(timezone.utc) + timedelta(hours=7)


def parse_interval(interval: str) -> int:
    """Convert interval string (e.g. '15m', '1h') to seconds."""
    interval = interval.strip().lower()
    if interval.endswith("m"):
        return int(interval[:-1]) * 60
    elif interval.endswith("h"):
        return int(interval[:-1]) * 3600
    elif interval.endswith("d"):
        return int(interval[:-1]) * 86400
    raise ValueError(f"Unsupported interval: {interval}")


def main():
    parser = argparse.ArgumentParser(description="Always-on candle pattern monitor")
    parser.add_argument("--symbols", type=str,
                        default=os.getenv("WATCHLIST_SYMBOLS", "BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT"))
    parser.add_argument("--interval", type=str, default=os.getenv("INTERVAL", "15m"))
    parser.add_argument("--price-report-interval", type=str, default="1h")
    parser.add_argument("--price-report-enabled", action="store_true", default=True)
    parser.add_argument("--dry-run", action="store_true", help="Print alerts without sending to Telegram")
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    check_seconds = parse_interval(args.interval)
    price_report_seconds = parse_interval(args.price_report_interval)

    print(f"\n{'='*60}")
    print(f"  Candle Pattern Monitor — Always-On Mode")
    print(f"{'='*60}")
    print(f"  Symbols: {', '.join(symbols)}")
    print(f"  Pattern check interval: {args.interval} ({check_seconds}s)")
    print(f"  Price report interval:  {args.price_report_interval} ({price_report_seconds}s)")
    print(f"  Start time: {utc_plus_7().strftime('%Y-%m-%d %H:%M:%S UTC+7')}")
    print(f"  Ctrl+C to stop\n")
    print(f"{'='*60}\n")

    load_env()

    # Initialize clients
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    binance_key = os.getenv("BINANCE_API_KEY")

    binance_client = BinanceClient(binance_key) if binance_key else BinanceClient()

    bot = None
    if telegram_token and telegram_chat_id:
        bot = TelegramBot(telegram_token, telegram_chat_id)
        print(f"✅ Telegram bot initialized (chat: {telegram_chat_id})")
    else:
        print(f"⚠️  Telegram not configured — running in dry-run mode")
        args.dry_run = True

    last_alert = {s: None for s in symbols}  # Track last alert per symbol
    last_price_report = time.time() - price_report_seconds  # Force immediate first report

    # Send initial price report
    tickers = []
    for symbol in symbols:
        t = binance_client.get_price_ticker(symbol)
        if t:
            tickers.append(t)
            print(f"  ✅ {symbol}: ${t['price']} ({t['price_change_pct']:+.2f}%)")
        else:
            print(f"  ❌ {symbol}: fetch failed")

    if tickers and bot and not args.dry_run:
        ts = utc_plus_7().strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")
        report = format_price_report(tickers, timestamp=ts)
        sent = bot.send_message(report)
        print(f"\n📨 Initial price report sent: {sent}")
    elif tickers and args.dry_run:
        ts = utc_plus_7().strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")
        report = format_price_report(tickers, timestamp=ts)
        print(f"\n📝 Price report (dry-run):\n{report}")

    last_price_report = time.time()

    # Main loop
    print(f"\n{'='*60}")
    print(f"  Monitoring started. Next check in {args.interval}.")
    print(f"  Price report in {args.price_report_interval}.")
    print(f"{'='*60}\n")

    try:
        while True:
            current_time = time.time()

            # ─── Pattern Monitoring ───────────────────────────────
            for symbol in symbols:
                try:
                    candles = binance_client.get_klines(symbol, args.interval, limit=50)
                    if not candles:
                        continue

                    # Filter to closed candles only
                    candles = [c for c in candles if c.is_closed]
                    if len(candles) < 3:
                        continue

                    patterns = detect_patterns(candles)
                    latest = candles[-1]

                    if patterns:
                        ts = utc_plus_7().strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")
                        alert = format_pattern_alert(symbol, args.interval, patterns, latest, timestamp=ts)

                        # Avoid duplicate alerts for the same candle
                        ts_key = latest.close_time
                        if ts_key == last_alert[symbol]:
                            continue

                        last_alert[symbol] = ts_key

                        if args.dry_run or not bot:
                            print(f"\n{'='*60}")
                            print(f"  PATTERN ALERT (dry-run)")
                            print(f"{'='*60}")
                            print(alert)
                            print()
                        elif bot:
                            sent = bot.send_message(alert)
                            print(f"[{ts}] 📨 Alert sent for {symbol}: "
                                  f"{', '.join(p['name'] for p in patterns)} "
                                  f"(sent={sent})")

                except Exception as e:
                    print(f"[{utc_plus_7().strftime('%H:%M:%S UTC+7')}] ❌ Error checking {symbol}: {e}")

            # ─── Periodic Price Report ─────────────────────────────
            if current_time - last_price_report >= price_report_seconds:
                if args.price_report_enabled:
                    try:
                        tickers = []
                        for symbol in symbols:
                            t = binance_client.get_price_ticker(symbol)
                            if t:
                                tickers.append(t)

                        if tickers:
                            ts = utc_plus_7().strftime("%Y-%m-%d %H:%M:%S UTC+7 (%H:%M UTC)")
                            report = format_price_report(tickers, timestamp=ts)

                            if args.dry_run or not bot:
                                print(f"\n{'='*60}")
                                print(f"  PRICE REPORT (dry-run)")
                                print(f"{'='*60}")
                                print(report)
                                print()
                            elif bot:
                                sent = bot.send_message(report)
                                print(f"[{ts}] 📊 Price report sent: {sent}")

                        last_price_report = current_time

                    except Exception as e:
                        print(f"[{utc_plus_7().strftime('%H:%M:%S UTC+7')}] ❌ Price report error: {e}")

            # ─── Sleep until next cycle ─────────────────────────────
            # Sleep for the smaller of (next pattern check, next price report)
            next_pattern = check_seconds
            remaining_price = price_report_seconds - (current_time - last_price_report)
            sleep_time = min(next_pattern, max(0, remaining_price))
            sleep_time = max(1, min(sleep_time, 3600))  # Cap at 1 hour

            time.sleep(sleep_time)

    except KeyboardInterrupt:
        print(f"\n{'='*60}")
        print(f"  Monitor stopped by user")
        print(f"  Stopped at: {utc_plus_7().strftime('%Y-%m-%d %H:%M:%S UTC+7')}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
