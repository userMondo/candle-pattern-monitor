# Cloudflare Workers Deployment Guide

## Prerequisites

1. **Cloudflare account** (free tier): https://dash.cloudflare.com/sign-up
2. **Wrangler CLI** (Cloudflare's CLI tool)

## Step 1: Install Wrangler

```bash
npm install -g wrangler
```

## Step 2: Authenticate

```bash
wrangler auth login
```

This opens a browser window — log in to your Cloudflare account.

## Step 3: Set Up Secrets

**Only 2 secrets are required.** The Binance API key is optional (not needed — public endpoints work without it):

```bash
cd src-worker

# REQUIRED: Telegram bot token
wrangler secret put TELEGRAM_BOT_TOKEN
# Paste your current bot token (get from @BotFather)

# REQUIRED: Telegram chat ID
wrangler secret put TELEGRAM_CHAT_ID
# Paste: 6580853770 (or your own chat ID)

# OPTIONAL: Binance API key (for higher rate limits — NOT required)
wrangler secret put BINANCE_API_KEY
```

> **Data source**: The worker gets all crypto data from Binance's **public** REST API (`api.binance.com/api/v3/klines` and `/api/v3/ticker/24hr`). No API key needed — it only helps with rate limits.

## Step 4: Configure Variables (Optional)

```bash
# Override default symbols (optional)
wrangler var put WATCHLIST_SYMBOLS --binding WATCHLIST_SYMBOLS --value "BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT"

# Override default interval
wrangler var put INTERVAL --binding INTERVAL --value "15m"
```

## Step 5: Deploy

```bash
wrangler deploy
```

## Step 6: Verify

After deployment, you'll get a URL like `https://candle-pattern-monitor.<account>.workers.dev`.

Test the endpoints:

```bash
# Health check
curl https://<your-sub>.workers.dev/health

# Manual pattern check
curl https://<your-sub>.workers.dev/run

# Manual price report
curl https://<your-sub>.workers.dev/price-report
```

## Schedule (Automatic)

After deployment, Cloudflare automatically runs:
- **Pattern monitor**: `*/15 * * * *` (every 15 minutes at exact second) → checks all patterns + sends Telegram alerts
- **Price report**: `5 * * * *` (at :05 past each hour) → sends hourly 24h price summary

These are defined in `wrangler.toml` under `[triggers]`.

## Local Development

```bash
# Run locally with Wrangler dev server
wrangler dev

# Test with curl
curl http://localhost:8787/run
curl http://localhost:8787/price-report
curl http://localhost:8787/health
```

## Pricing

Free tier includes:
- 100,000 requests/day (your cron uses ~97 daily → well within free tier)
- Cron triggers (up to 5 per worker)
- 100% free, no credit card required

## Monitoring

Check logs:
```bash
wrangler tail
```
