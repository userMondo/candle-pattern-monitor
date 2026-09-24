# Candle Pattern Monitor

A zero-cost, 24/7 candlestick pattern monitoring system that detects reversal patterns on major crypto pairs and sends alerts via Telegram. Hosted entirely on GitHub Actions using the Binance public API.

## Features

- **Zero-cost hosting**: Runs entirely on GitHub Actions free tier
- **Patterns**: All 13+ pattern detectors active by default (Engulfing, Doji, Hammer, Shooting Star, Pinbar, Morning/Evening Star, Doji+Engulfing) — filter with `--focus` if needed
- **Telegram alerts**: Instant notifications with pattern details, UTC+7 timestamps, and percentage strength
- **Hourly price reports**: Summary of 24h price changes for all monitored pairs
- **Dynamic watchlist**: Configurable via CLI args, environment variables, or GitHub Actions inputs
- **Multiple timeframes**: Supports 15m, 1h, and 4h intervals
- **Auto-triggered**: Pattern alerts every 15min/1h/4h + price report hourly

## Quick Start

> This project requires no local installation — it runs on GitHub Actions.

### Prerequisites

1. GitHub account (free)
2. Telegram bot token and chat ID (free from [@BotFather](https://t.me/BotFather))

### Setup

1. **Clone this repository:**
   ```bash
   git clone https://github.com/userMondo/candle-pattern-monitor.git
   cd candle-pattern-monitor
   ```

2. **Add GitHub Actions secrets** in repo Settings → Secrets and Variables → Actions:
   - `TELEGRAM_BOT_TOKEN` — Your Telegram bot token
   - `TELEGRAM_CHAT_ID` — Your Telegram chat ID (see `src/get_chat_id.py` helper)
   - `BINANCE_API_KEY` — (optional, for higher rate limits)

3. **Trigger a manual run** to verify:
   - Go to https://github.com/userMondo/candle-pattern-monitor/actions
   - Click "Candle Pattern Monitor" → "Run workflow" → "Run workflow"
   - Check the step output for "Alert sent: True"

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WATCHLIST_SYMBOLS` | Comma-separated trading pairs | `BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token | *(required for alerts)* |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for alerts | *(required for alerts)* |
| `INTERVAL` | Default kline interval | `15m` |
| `PATTERN_FOCUS` | Pattern categories (leave empty for ALL) | *(empty = all patterns)* |
| `CANDLE_LIMIT` | Number of candles to fetch per symbol | `50` |
| `BINANCE_API_KEY` | Binance API key (optional) | *(optional)* |

### Cron Schedule (UTC)

| Workflow | Schedule | Description | Local (UTC+7) |
|----------|----------|-------------|----------------|
| Pattern Monitor | `*/15 * * * *` | All patterns on 15m interval | Every 15 min (offset +7h) |
| Pattern Monitor | `0 * * * *` | All patterns on 1h interval | Hourly |
| Pattern Monitor | `0 */4 * * *` | All patterns on 4h interval | Every 4h (11:00, 15:00, 19:00, 23:00) |
| Price Report | `5 * * * *` | Hourly price summary for all pairs | Hourly (at :37 local) |

> **Note**: GitHub Actions cron fires within a ±15 minute window, not at exact minute marks.

### Supported Intervals

- `15m` — 15 minutes (primary monitoring)
- `1h` — 1 hour
- `4h` — 4 hours

### Supported Pairs

Any trading pair available on Binance. Default watchlist:
- `BTCUSDT` — Bitcoin
- `NEARUSDT` — NEAR Protocol
- `ZECUSDT` — Zcash
- `PAXGUSDT` — Gold-backed token (PAX Gold)

## Pattern Focus

Default focus: **all patterns** (no filtering). Use `--focus` to limit which patterns are detected:

| Category | Patterns |
|----------|----------|
| `engulfing` | Bullish/Bearish Engulfing, Doji + Engulfing |
| `doji` | Doji, Doji + Engulfing |
| `pinbar` | Bullish/Bearish Pinbar |
| `hammer` | Hammer, Hanging Man |
| `shooting_star` | Shooting Star, Inverted Hammer |
| `morning_star` | Morning Star |
| `evening_star` | Evening Star |

### Alert Format

Pattern alerts include:
- UTC+7 timestamp (also shows UTC)
- Percentage strength (e.g. 67% for 2/3, 100% for 3/3)
- Price change percentage (open → close)
- Body size and wick percentages relative to total range
- Direction icons (green/red)

### Price Report

The hourly price report (`/1h` interval) sends a summary of all monitored pairs:

```
📈 Hourly Price Report
Time (UTC+7): 2024-01-01 12:00:00 UTC+7 (05:00 UTC)

Pair           Price         24h Δ         Range          Vol
BTCUSDT     83,316.01 🔴-2.94%  H:85966.04 L:82874.93 V:22746.80
NEARUSDT      4.206000 🔴-7.46%  H:    4.80 L:    4.03 V:77851835.30
```

## Project Structure

```
candle-pattern-monitor/
├── .github/
│   └── workflows/
│       ├── candle_monitor.yml    # Pattern monitoring cron (*/15, hourly, 4h)
│       └── price_report.yml      # Hourly price report cron (5 * * * *)
├── src/
│   ├── __init__.py
│   ├── binance_client.py         # Binance API client with endpoint fallback
│   ├── patterns.py               # 13+ pattern detectors + alert formatters
│   ├── telegram_bot.py           # Telegram notification client
│   └── get_chat_id.py            # Helper to find Telegram chat ID
├── tests/
│   ├── __init__.py
│   └── test_patterns.py          # 31 unit tests
├── .env.example                  # Config template
├── .gitignore
├── README.md
├── main.py                       # CLI entry point (--price-report mode)
├── progress_tracker.md
├── SECRETS_SETUP_GUIDE.md        # Step-by-step secrets setup
└── TELEGRAM_SETUP_GUIDE.md
```

## Development

### Local Testing

```bash
pip install requests pytest

# Run tests (31 tests)
python -m pytest tests/ -v

# Run pattern monitoring (all patterns by default)
python main.py --symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT --interval 15m

# Run price report
python main.py --symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT --interval 1h --price-report

# Focus on specific patterns only
python main.py --symbols BTCUSDT --interval 15m --focus engulfing,doji
```

### Finding Your Telegram Chat ID

```bash
python3 src/get_chat_id.py --token YOUR_BOT_TOKEN
```

## License

MIT
