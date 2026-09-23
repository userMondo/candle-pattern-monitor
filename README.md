# Candle Pattern Monitor

A zero-cost, 24/7 candlestick pattern monitoring system that detects reversal patterns on major crypto pairs and sends alerts via Telegram. Hosted entirely on GitHub Actions using the Binance public API.

## Features

- **Zero-cost hosting**: Runs entirely on GitHub Actions free tier
- **Patterns**: All 13+ pattern detectors active by default (Engulfing, Doji, Hammer, Shooting Star, Pinbar, Morning/Evening Star, Doji+Engulfing) — filter with `--focus` if needed
- **Telegram alerts**: Instant notifications with pattern details
- **Dynamic watchlist**: Configurable via GitHub Actions repository variables
- **Multiple timeframes**: Supports 15m, 1h, and 4h intervals
- **Auto-triggered**: Runs every 15 minutes (primary patterns), hourly + every 4 hours (full scan), plus manual dispatch

## Quick Start

> This project requires no local installation — it runs on GitHub Actions. Setup takes 3 minutes.

### Prerequisites

1. GitHub account (free)
2. Telegram bot token and chat ID (free from [@BotFather](https://t.me/BotFather))

### Setup

1. **Fork or clone this repository:**
   ```bash
   git clone https://github.com/userMondo/candle-pattern-monitor.git
   cd candle-pattern-monitor
   ```

2. **Set up GitHub Actions secrets** in your repo Settings → Secrets and Variables → Actions:
   - `TELEGRAM_BOT_TOKEN` — Your Telegram bot token
   - `TELEGRAM_CHAT_ID` — Your Telegram chat ID (see `src/get_chat_id.py` helper)

3. **Configure watchlist** (optional):
   - Add a repository variable `WATCHLIST_SYMBOLS` (comma-separated)
   - Default: `BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT`

4. **Run manually or wait for cron:**
   - Every 15 minutes (`*/15 * * * *`) — all patterns on 15m interval (note: GitHub fires within ~±15 min window, not at exact minute marks)
   - **Hourly cron**: `0 * * * *` — all patterns on 1h interval
   - **4-hour cron**: `0 */4 * * *` — all patterns on 4h interval
   - Or trigger manually: Actions tab → candle_monitor → Run workflow

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WATCHLIST_SYMBOLS` | Comma-separated trading pairs | `BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token | *(required)* |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for alerts | *(required)* |
|| `INTERVAL` | Default kline interval | `15m` |
|| `PATTERN_FOCUS` | Pattern categories (leave empty for ALL) | *(empty = all patterns)* |
| `CANDLE_LIMIT` | Number of candles to fetch per symbol | `50` |
| `BINANCE_API_KEY` | Binance API key (optional) | *(optional)* |

### Supported Intervals

- `15m` — 15 minutes (primary monitoring)
- `1h` — 1 hour
- `4h` — 4 hours

### Supported Pairs

Any trading pair available on Binance. Monitored pairs:
- `BTCUSDT` — Bitcoin
- `NEARUSDT` — NEAR Protocol
- `ZECUSDT` — Zcash
- `PAXGUSDT` — Gold-backed token (PAX Gold / Tether Gold proxy)

> Note: HYPE is not listed on Binance. Gold is available as `PAXGUSDT` or `XAUTUSDT`.

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

Default focus: `engulfing,doji` (primary patterns only).

## Candlestick Patterns Detected

| Pattern | Category | Direction | Description |
|---------|----------|-----------|-------------|
| Bullish Engulfing | engulfing | bullish | Large bullish candle engulfs previous bearish candle |
| Bearish Engulfing | engulfing | bearish | Large bearish candle engulfs previous bullish candle |
| Doji | doji | neutral | Open == close (market indecision) |
| Doji + Bullish Engulfing | doji, engulfing | bullish | Doji after downtrend + strong bullish engulfing (strength: 3/3) |
| Doji + Bearish Engulfing | doji, engulfing | bearish | Doji after uptrend + strong bearish engulfing (strength: 3/3) |
| Hammer | hammer | bullish | Small body at top with long lower wick |
| Hanging Man | hammer | bearish | Hammer pattern in uptrend |
| Shooting Star | shooting_star | bearish | Small body at bottom with long upper wick |
| Inverted Hammer | shooting_star | bullish | Shooting star pattern in downtrend |
| Bullish Pinbar | pinbar | bullish | Long lower wick with small body at top |
| Bearish Pinbar | pinbar | bearish | Long upper wick with small body at bottom |
| Morning Star | morning_star | bullish | 3-candle bullish reversal |
| Evening Star | evening_star | bearish | 3-candle bearish reversal |

## Project Structure

```
candle-pattern-monitor/
├── .github/
│   └── workflows/
│       └── candle_monitor.yml       # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── binance_client.py            # Binance klines REST API client
│   ├── patterns.py                  # 13+ pattern detectors including Doji+Engulfing
│   ├── telegram_bot.py              # Telegram notification client
│   └── get_chat_id.py               # Helper to find Telegram chat ID
├── tests/
│   ├── __init__.py
│   └── test_patterns.py            # 29 pattern detection tests
├── .env.example                     # Config template
├── .gitignore
├── README.md
├── main.py                          # CLI entry point
└── progress_tracker.md
```

## Development

### Local Testing

```bash
# Install dependencies
pip install requests pytest

# Run pattern tests (29 tests)
python -m pytest tests/ -v

# Run monitor manually (all patterns by default)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python main.py --symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT --interval 15m
```

### Finding Your Telegram Chat ID

```bash
# After messaging your bot with /start:
python3 src/get_chat_id.py --token YOUR_BOT_TOKEN
```

## License

MIT
