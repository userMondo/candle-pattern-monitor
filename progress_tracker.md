# Candle Pattern Monitor - Progress Tracker

> Project: Candle Pattern Monitor Agent
> Repo: https://github.com/userMondo/candle-pattern-monitor.git
> Created: 2026-09-21

## Overview
Build a zero-cost, 24/7 candlestick pattern monitoring system on GitHub Actions that detects
all 13+ reversal patterns on crypto pairs and sends Telegram alerts.

## Status: Active Development

### Completed
- [x] Project initialized and cloned from GitHub
- [x] `src/binance_client.py` — Binance klines API client (no auth needed, public endpoint)
- [x] `src/patterns.py` — Pattern detection (13 pattern types including Engulfing, Doji, Doji+Engulfing)
- [x] `src/telegram_bot.py` — Telegram Bot API client
- [x] `src/get_chat_id.py` — Helper to find Telegram chat ID
- [x] `tests/test_patterns.py` — 31 unit tests (all passing)
- [x] `.github/workflows/candle_monitor.yml` — Pattern monitoring cron (*/15, hourly, 4h)
- [x] `.github/workflows/price_report.yml` — Hourly price report cron (5 * * * *)
- [x] `SECRETS_SETUP_GUIDE.md` — Step-by-step GitHub secrets setup guide
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
| **Pattern focus** | All 13+ patterns by default (Engulfing, Doji, Doji+Engulfing, Hammer, Hanging Man, Shooting Star, Inverted Hammer, Bull/Bear Pinbar, Morning Star, Evening Star) |
| **Binance API key** | `<REDACTED>` — ✅ valid, verified live |
| **Telegram bot** | `@jiodsjfiebot` (Aritoria) — ✅ token valid |
| **Telegram alerts** | ✅ LIVE — test message + pattern alerts sent |

## Pattern Focus

Default focus: **all patterns** (no filtering). Use `--focus` or `PATTERN_FOCUS` env var to limit which patterns are detected.

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

**2026-09-22 — GitHub Actions workflow fix**
- Fixed `main.py` to handle missing Telegram credentials gracefully (workflow was crashing when secrets weren't set)
- Manual workflow run succeeded (2026-09-22T15:51:22Z — ✅ conclusion=success)
- Workflow now runs every 15m/hourly/4h without crashing
- Once GitHub secrets are added (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID), alerts will fire automatically

**2026-09-22 — GitHub workflow pushed**
- PAT now has `workflow` scope — workflow file pushed successfully (commit `a8f14b9`)
- All 11+ tracked files verified on GitHub remote

**2026-09-24 — Alert message upgrade + hourly price report**
- Enhanced `format_pattern_alert` with:
  - UTC+7 timestamp (converted from candle close_time, also shows UTC)
  - Percentage strength (strength/3 → %, e.g. 67% for 2/3, 100% for 3/3, 33% for 1/3)
  - Price change percentage (open→close)
  - Body size and wick percentages relative to total range
  - Direction icons (green/red for bullish/bearish)
- Added `format_price_report()` — hourly price summary for all watched symbols
- Added `--price-report` CLI flag and `run_price_report()` function
- Added separate workflow `price_report.yml` — runs at `5 * * * *` (hourly, staggered)
- Added Binance endpoint fallbacks (`api.binance.com` + `api.binance.us`) to handle HTTP 451 IP blocking on GitHub Actions
- Added `get_price_ticker()` and `get_server_time()` methods to `BinanceClient`
- All 31/31 tests pass

**2026-09-23 — Security cleanup**
- Root cause found: GitHub secrets NOT set → workflow skips Telegram
- Wrong Telegram token in `.env` (old/revoked) → FIXED, correct token verified
- Binance API returning HTTP 451 (IP blocked) from GitHub Actions → FIXED with endpoint fallback
- Redacted all real secrets from `TELEGRAM_SETUP_GUIDE.md` and `progress_tracker.md`
- Created `SECRETS_SETUP_GUIDE.md` — step-by-step guide for adding GitHub secrets

## Verification Summary

### Passed
- ✅ 31/31 pytest tests pass (29 original + 2 new alert format tests)
- ✅ All 13+ pattern detectors verified (Engulfing, Doji, Doji+Engulfing, Hammer, Hanging Man, Shooting Star, Inverted Hammer, Bull/Bear Pinbar, Morning Star, Evening Star)
- ✅ All-patterns monitoring active by default (DEFAULT_FOCUS = None)
- ✅ Pattern focus filtering works correctly (--focus flag, PATTERN_FOCUS env)
- ✅ Binance API: BTCUSDT, NEARUSDT, ZECUSDT, PAXGUSDT at 15m/1h/4h (live data)
- ✅ Pattern detection: all patterns tested via unit tests + live data
- ✅ TelegramBot: code verified, live alerts sent successfully
- ✅ Telegram token: valid (Aritoria / @jiodsjfiebot)
- ✅ Telegram chat ID: valid (messages received)
- ✅ GitHub: 9+ commits pushed, all files verified on remote
- ✅ GitHub Actions: 9+ post-fix scheduled runs all succeed ✅
- ✅ Alert format: UTC+7 timestamps, percentage strength, candle details
- ✅ `.gitignore`: clean (does not exclude workflow files)
- ✅ `.env.example`: no real secrets (all placeholders)
- ✅ No real secrets in tracked files
- ✅ `.env` has correct credentials (git-ignored, token verified valid)
- ✅ `SECRETS_SETUP_GUIDE.md`: step-by-step guide for adding secrets

### Blocked — User Action Required
- ❌ **GitHub secrets**: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` not set as repo secrets (PAT can't create secrets) — add via GitHub UI Settings → Secrets & Variables → Actions

### Fixed This Round
- ✅ **Cron empty inputs**: GitHub `schedule` events pass empty strings for `workflow_dispatch` inputs — FIXED with bash fallback defaults in workflow (commit `75e1959`)

## Key Commands

```bash
# Run tests
PYTHONPATH=src python -m pytest tests/ -v

# Run monitor locally (all patterns by default)
python main.py --symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT --interval 15m

# Or focus on specific patterns only
python main.py --symbols BTCUSDT --interval 15m --focus engulfing,doji

# Find Telegram chat ID (already discovered)
# Token: <redacted> (hamble / @jiodsjfiebot)
# Chat ID: <redacted>

# Add to GitHub secrets via UI: Settings → Secrets & Variables → Actions
#   TELEGRAM_BOT_TOKEN = <your_token>
#   TELEGRAM_CHAT_ID = <your_chat_id>
#   BINANCE_API_KEY = <your_key>

# Push changes (if PAT has workflow scope)
git add -A && git commit -m "update" && git push origin main
```
