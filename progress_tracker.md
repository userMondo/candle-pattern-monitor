# Candle Pattern Monitor - Progress Tracker

> Project: Candle Pattern Monitor Agent
> Repo: https://github.com/userMondo/candle-pattern-monitor.git
> Created: 2026-09-21

## Overview
24/7 candlestick pattern monitoring system on **Cloudflare Workers** — detects 13+ patterns across 15m/1h/4h intervals and sends Telegram alerts with UTC+7 timestamps and percentage strength. Zero cost, exact-second cron precision.

## Status: Live ✅ (Cloudflare Workers — all intervals working)

### Completed
- [x] `src-worker/index.ts` — Worker entry point with multi-interval cron routing
- [x] `src-worker/patterns.ts` — 13+ pattern detectors + alert/price formatters (TS port)
- [x] `src-worker/binanceClient.ts` — Binance API client with User-Agent fix
- [x] `src-worker/telegramBot.ts` — Telegram Bot API client
- [x] `src-worker/types.ts` — Shared TypeScript interfaces
- [x] `src-worker/wrangler.toml` — Single cron trigger: `*/15 * * * *`

### Cron Schedule (Single trigger with time-based routing)

| Cron time | What runs | Interval |
|-----------|-----------|----------|
| `*:00, *:15, *:30, *:45` | Pattern check | `15m` |
| `*:00` (every hour) | Price report (all pairs 24h summary) | — |
| `*:15` (every hour) | Pattern check | `1h` |
| `*:30` (at 00/04/08/12/16/20 UTC) | Pattern check | `4h` |

### Live Verification ✅

| Check | Result |
|-------|--------|
| TypeScript tests | 11/11 pass |
| Health check | 200 OK |
| 15m patterns | 1 alert sent (Bearish Pinbar BTCUSDT) |
| 1h patterns | 1 alert sent (Bearish Pinbar ZECUSDT) |
| 4h patterns | 1 alert sent (Bullish Engulfing + Pinbar BTCUSDT) |
| Price report | sent=true, 4 tickers |
| Cron trigger | `*/15 * * * *` confirmed |
| GitHub Actions | Schedule DISABLED (manual only) |

### Worker URL
`https://candle-pattern-monitor.phetmesy.workers.dev`

### Secrets Set
- `TELEGRAM_BOT_TOKEN` ✅
- `TELEGRAM_CHAT_ID` = 6580853770 ✅
- `BINANCE_API_KEY` ✅

### Key Commands
```bash
cd src-worker
npx vitest run          # Test (11 tests)
wrangler deploy         # Deploy updates
wrangler tail           # View real-time logs
# Manual endpoints:
curl https://candle-pattern-monitor.phetmesy.workers.dev/run?interval=1h
curl https://candle-pattern-monitor.phetmesy.workers.dev/price-report
```
