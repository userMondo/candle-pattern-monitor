# Candle Pattern Monitor - Progress Tracker

> Project: Candle Pattern Monitor Agent
> Repo: https://github.com/userMondo/candle-pattern-monitor.git
> Created: 2026-09-21

## Overview
Build a zero-cost, 24/7 candlestick pattern monitoring system on **Cloudflare Workers** that detects
all 13+ reversal patterns on crypto pairs and sends Telegram alerts with UTC+7 timestamps and percentage strength.

## Status: Live on Cloudflare Workers ✅

### Completed
- [x] `src-worker/index.ts` — Worker entry point with cron handlers (pattern monitor + price report)
- [x] `src-worker/patterns.ts` — 13+ pattern detectors + alert/price formatters (TypeScript port)
- [x] `src-worker/binanceClient.ts` — Binance API client with User-Agent fix for 403 bypass
- [x] `src-worker/telegramBot.ts` — Telegram Bot API client
- [x] `src-worker/types.ts` — Shared TypeScript interfaces
- [x] `src-worker/wrangler.toml` — Cron triggers: `*/15 * * * *` + `5 * * * *`
- [x] `src-worker/test/patterns.test.ts` — 11 TypeScript unit tests (100% pass)
- [x] `src-worker/DEPLOY.md` — Step-by-step deployment guide
- [x] Deployed to `https://candle-pattern-monitor.phetmesy.workers.dev`
- [x] Telegram bot: `@jiodsjfiebot` (Aritoria) — valid, alerts confirmed received
- [x] Telegram chat ID: 6580853770 — confirmed receiving alerts
- [x] Cloudflare secrets: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, BINANCE_API_KEY (all set)
- [x] Pattern alerts: UTC+7 timestamps, % strength, candle details (Open/Close/High/Low/Body/Wicks)
- [x] Hourly price report: 24h change, range, volume for all 4 pairs
- [x] GitHub Actions: cron schedules disabled (kept for manual `workflow_dispatch` only)

### Also Complete (legacy Python codebase)
- [x] `src/binance_client.py` — Binance klines API client (Python)
- [x] `src/patterns.py` — 31 Python unit tests (all passing)
- [x] `main.py` — Python CLI entry point with `--price-report` mode
- [x] `.env.example`, `.gitignore`, `progress_tracker.md`

## Configuration

| Setting | Value |
|---------|-------|
| **Symbols** | `BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` |
| **Pattern cron** | `*/15 * * * *` (exact second, UTC) |
| **Price report cron** | `5 * * * *` (hourly, UTC) |
| **Interval** | `15m` (primary), `1h`, `4h` |
| **Pattern focus** | All 13+ patterns by default |
| **Telegram bot** | `@jiodsjfiebot` (Aritoria) |

## Cron Schedules (Cloudflare Workers — Exact Second Precision)

| Cron | Frequency | What it does |
|------|-----------|-------------|
| `*/15 * * * *` | Every 15 min | Pattern detection + Telegram alerts |
| `5 * * * *` | Hourly (:05) | Price report for all pairs |

> Unlike GitHub Actions (±15 min variance), Cloudflare fires crons at the exact second.

## Key Commands

```bash
# ─── Cloudflare Workers (ACTIVE) ──────────────────────────────
cd src-worker

# Run TypeScript tests (11 tests)
npx vitest run

# Manual endpoint testing
curl https://candle-pattern-monitor.phetmesy.workers.dev/health
curl https://candle-pattern-monitor.phetmesy.workers.dev/run
curl https://candle-pattern-monitor.phetmesy.workers.dev/price-report

# Deploy updates
wrangler deploy

# View real-time logs
wrangler tail

# ─── Python (GitHub Actions — DISABLED) ───────────────────────
# Run tests
PYTHONPATH=src python -m pytest tests/ -v

# Run monitor locally
python main.py --symbols BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT --interval 15m
```

## Deployment Steps (one-time)

```bash
cd src-worker
wrangler login                              # Browser auth (one-time)
wrangler secret put TELEGRAM_BOT_TOKEN      # Your bot token
wrangler secret put TELEGRAM_CHAT_ID        # 6580853770
wrangler secret put BINANCE_API_KEY         # Optional
wrangler deploy                             # Deploy with cron triggers
```
