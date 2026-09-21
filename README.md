# Candle Pattern Monitor

A zero-cost, 24/7 candlestick pattern monitoring system that detects reversal patterns on major crypto pairs and sends alerts via Telegram. Hosted entirely on GitHub Actions using Binance public API.

## Features

- **Zero-cost hosting**: Runs entirely on GitHub Actions free tier
- **Pattern detection**: Engulfing, Hammer, Shooting Star, Doji, Pinbar, Morning Star, Evening Star
- **Telegram alerts**: Instant notifications with pattern details
- **Dynamic watchlist**: Configurable via GitHub Actions repository variables
- **Multiple timeframes**: Supports 1h and 4h intervals
- **Auto-triggered**: Runs every 4 hours via cron, also supports manual dispatch

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
   - `TELEGRAM_CHAT_ID` — Your Telegram chat ID

3. **Configure watchlist** (optional):
   - Add a repository variable `WATCHLIST_SYMBOLS` (comma-separated, e.g., `BTCUSDT,ETHUSDT,SOLUSDT`)
   - Default: `BTCUSDT,ETHUSDT,SOLUSDT`

4. **Run manually or wait for cron:**
   - The workflow triggers automatically every 4 hours (`0 */4 * * *`)
   - Or trigger manually: Actions tab → candle_monitor → Run workflow

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WATCHLIST_SYMBOLS` | Comma-separated trading pairs | `BTCUSDT,ETHUSDT,SOLUSDT` |
| `TELEGRAM_BOT_TOKEN` | Telegram bot API token | *(required)* |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for alerts | *(required)* |
| `BINANCE_API_KEY` | Binance API key (optional, for rate limits) | *(optional)* |

### Supported Intervals

- `1h` — 1 hour
- `4h` — 4 hours

### Supported Pairs

Any trading pair available on Binance (e.g., `BTCUSDT`, `ETHUSDT`, `SOLUSDT`, `ADAUSDT`, etc.)

## Candlestick Patterns Detected

| Pattern | Type | Description |
|---------|------|-------------|
| Engulfing | Reversal | Large candle engulfs previous candle |
| Hammer | Reversal | Small body near top with long lower wick |
| Shooting Star | Reversal | Small body near bottom with long upper wick |
| Doji | Reversal | Open == Close (indecision) |
| Pinbar | Reversal | Long wick with small body |
| Morning Star | Reversal | 3-candle bullish reversal pattern |
| Evening Star | Reversal | 3-candle bearish reversal pattern |

## Project Structure

```
candle-pattern-monitor/
├── .github/
│   └── workflows/
│       └── candle_monitor.yml       # GitHub Actions workflow
├── src/
│   ├── __init__.py
│   ├── patterns.py                  # Pattern detection logic
│   ├── binance_client.py            # Binance API client
│   └── telegram_bot.py              # Telegram notification sender
├── tests/
│   ├── __init__.py
│   └── test_patterns.py            # Pattern detection tests
├── main.py                          # Entry point
├── progress_tracker.md              # Development progress tracking
└── README.md
```

## Development

### Local Testing

```bash
# Install dependencies
pip install requests

# Run pattern tests
python -m pytest tests/ -v

# Run monitor manually (requires TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID)
export TELEGRAM_BOT_TOKEN="your_bot_token"
export TELEGRAM_CHAT_ID="your_chat_id"
python main.py --symbols BTCUSDT,ETHUSDT --interval 4h
```

## License

MIT
