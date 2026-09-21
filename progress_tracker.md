# Candle Pattern Monitor - Progress Tracker

> Project: Candle Pattern Monitor Agent
> Repo: https://github.com/userMondo/candle-pattern-monitor.git
> Created: 2026-09-21

## Overview
Build a zero-cost, 24/7 candlestick pattern monitoring system on GitHub Actions that detects
reversal patterns (Engulfing + Doji + Doji/Engulfing) on crypto pairs and sends Telegram alerts.

## Status: Active Development

### Completed
- [x] Project initialized and cloned from GitHub
- [x] `src/binance_client.py` — Binance klines API client (no auth needed, public endpoint)
- [x] `src/patterns.py` — Pattern detection (13 pattern types including Engulfing, Doji, Doji+Engulfing)
- [x] `src/telegram_bot.py` — Telegram Bot API client
- [x] `src/get_chat_id.py` — Helper to find Telegram chat ID
- [x] `main.py` — CLI entry point with `--interval`, `--symbols`, `--focus` args
- [x] `.github/workflows/candle_monitor.yml` — GitHub Actions cron (15m, hourly, 4h)
- [x] `.env.example` — Configuration template with placeholders
- [x] `tests/test_patterns.py` — 27 unit tests (all passing)
- [x] `README.md` — Full documentation

### In Progress
- [ ] Push remaining changes (workflow file blocked by PAT scope)

### Blocked
- GitHub push: PAT lacks `workflow` scope for `.github/workflows/` files

## Configuration

| Setting | Value |
|---------|-------|
| **Symbols** | `BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` |
| **Intervals** | `15m` (primary), `1h`, `4h` |
| **Primary patterns** | Engulfing, Doji, Doji + Engulfing |
| **Binance API key** | `HTvhNcdSX04zn3H1ilJv8bTaJSr8AKyn6GFbiZT76rRfNXKYpC82UhYfI0O3XrsE` (valid, optional) |
| **Telegram bot** | `@jiodsjfiebot` (bot: hamble) — ✅ token valid, needs `/start` message to get chat ID |

## Pattern Focus

Default focus: `engulfing,doji` — only detects Engulfing and Doji patterns.
Use `--focus all` or omit `--focus` to detect all patterns.

| Category | Patterns |
|----------|----------|
| `engulfing` | Bullish/Bearish Engulfing, Doji + Engulfing |
| `doji` | Doji, Doji + Engulfing |
| `pinbar` | Bullish/Bearish Pinbar |
| `hammer` | Hammer, Hanging Man |
| `shooting_star` | Shooting Star, Inverted Hammer |
| `morning_star` | Morning Star |
| `evening_star` | Evening Star |

## Progress Log

**2026-09-21 — Initial build complete**
- All source files created
- 21 unit tests passing (original set)
- GitHub repo initialized at `userMondo/candle-pattern-monitor`

**2026-09-22 — User refinements complete**
- Added Doji + Engulfing detector (3/3 strength, highest priority pattern)
- Added `focus` parameter to `detect_patterns()` for selective pattern detection
- Added `--focus` CLI argument and `PATTERN_FOCUS` env var
- Added `15m` interval support (verified Binance returns 100 candles for all symbols)
- Updated default symbols: `BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` (Gold = PAXG)
- HYPE not available on Binance — user can add if it lists later
- Updated GitHub Actions workflow with 3 cron schedules: `*/15 * * * *`, `0 * * * *`, `0 */4 * * *`
- Expanded tests to 27 (added 6 Doji+Engulfing and Focus tests)
- All 27 tests passing
- Fixed `.gitignore` (was incorrectly excluding workflow files)
- Redacted all secrets from tracked files
- First successful git push to GitHub (commit `28578ea`)
- GitHub workflow file can't be pushed via PAT (lacks `workflow` scope) — needs manual addition or PAT regeneration
- Telegram bot token invalid (401) — needs regeneration via @BotFather

**2026-09-22 — GitHub workflow pushed**
- PAT now has `workflow` scope — workflow file pushed successfully (commit `a8f14b9`)
- All 8+ tracked files verified on GitHub remote

**2026-09-22 — Telegram token update**
- New bot token `8800671132:***` is VALID — bot "hamble" (@jiodsjfiebot)
- Still needs user to message bot /start to generate chat ID
- Run `python3 src/get_chat_id.py --token 8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY` after messaging bot

## Verification Summary

### Passed
- ✅ 27/27 pytest tests pass
- ✅ Binance API: BTCUSDT, NEARUSDT, ZECUSDT, PAXGUSDT at 15m/1h/4h
- ✅ Pattern detection: Engulfing, Doji, Doji+Engulfing (tested via unit tests)
- ✅ TelegramBot: code formatting verified (mocked send)
- ✅ GitHub: code pushed to `https://github.com/userMondo/candle-pattern-monitor`
- ✅ `.gitignore`: clean (does not exclude workflow files)
- ✅ `.env.example`: no real secrets (all placeholders)
- ✅ No leaked secrets in tracked files

### Blocked — User Action Required
- ❌ **Telegram chat ID**: Unknown — message `@jiodsjfiebot` with `/start`, then run `python3 src/get_chat_id.py --token 8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY`

## Key Commands

```bash
# Run tests
PYTHONPATH=src python -m pytest tests/ -v

# Run monitor locally
python main.py --symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT --interval 15m --focus engulfing,doji

# Find Telegram chat ID (after messaging @jiodsjfiebot with /start)
python3 src/get_chat_id.py --token 8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY

# Push changes (if PAT has workflow scope)
git add -A && git commit -m "update" && git push origin main
```
