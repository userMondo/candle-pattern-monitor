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
| **Pattern focus** | All 13+ patterns by default (Engulfing, Doji, Doji+Engulfing, Hammer, Hanging Man, Shooting Star, Inverted Hammer, Bull/Bear Pinbar, Morning Star, Evening Star) |
| **Binance API key** | `HTvhNcdSX04zn3H1ilJv8bTaJSr8AKyn6GFbiZT76rRfNXKYpC82UhYfI0O3XrsE` ✅ valid, verified live |
| **Telegram bot** | `@jiodsjfiebot` (hamble) — ✅ token valid, chat ID: `6580853770` |
| **Telegram alerts** | ✅ LIVE — test message + Doji alert sent to chat 6580853770 |

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

**2026-09-22 — GitHub Actions schedule fix**
- Cron-triggered runs were FAILING — GitHub passes empty strings for `${{ inputs.xxx }}` when triggered by `schedule` (not `workflow_dispatch`)
- Fixed: added bash fallback in workflow (`if [ -z "$SYMBOLS" ]; then SYMBOLS="BTCUSDT,..."; fi`)
- Manual run (workflow_dispatch) at 18:13 UTC — ✅ succeeded with the fix
- Scheduled cron runs after 18:30 UTC will succeed with fallback defaults
- Commit: `75e1959`

## Verification Summary

### Passed
- ✅ 29/29 pytest tests pass (27 original + 2 new closed-candle tests)
- ✅ All 13+ pattern detectors verified (Engulfing, Doji, Doji+Engulfing, Pinbar, Hammer, Hanging Man, Shooting Star, Inverted Hammer, Morning Star, Evening Star)
- ✅ All-patterns monitoring active by default (no `--focus` = detect everything)
- ✅ Pattern focus filtering works correctly (engulfing-only, doji-only, etc.)
- ✅ Binance API: BTCUSDT, NEARUSDT, ZECUSDT, PAXGUSDT at 15m/1h/4h (live data)
- ✅ Pattern detection: Engulfing, Doji, Doji+Engulfing (tested via unit tests + live data)
- ✅ TelegramBot: code verified (live test message sent)
- ✅ Telegram token: valid (hamble / @jiodsjfiebot)
- ✅ Telegram chat ID: 6580853770 (discovered via getUpdates)
- ✅ GitHub: 7 commits pushed, all files verified on remote
- ✅ GitHub Actions: workflow runs successfully (manual run verified ✅)
- ✅ `.gitignore`: clean (does not exclude workflow files)
- ✅ `.env.example`: no real secrets (all placeholders)
- ✅ No leaked secrets in tracked files
- ✅ Local `.env` created with valid credentials (git-ignored)

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

# Find Telegram chat ID (already known: 6580853770)
# Token: 8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY
# Chat ID: 6580853770

# Add to GitHub secrets via UI: Settings → Secrets & Variables → Actions
#   TELEGRAM_BOT_TOKEN = 8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY
#   TELEGRAM_CHAT_ID = 6580853770
#   BINANCE_API_KEY = HTvhNcdSX04zn3H1ilJv8bTaJSr8AKyn6GFbiZT76rRfNXKYpC82UhYfI0O3XrsE

# Push changes (if PAT has workflow scope)
git add -A && git commit -m "update" && git push origin main
```
