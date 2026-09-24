# Cloudflare Workers — Action Required

## ⚠️ Temporary Account Limitations

The initial deployment used a temporary Cloudflare account which has limitations:
- ❌ **No cron triggers** (free tier limit of 0 on temp accounts)
- ❌ **No secrets** (must set on your real account)

## ✅ What works on the temporary deployment

- HTTP endpoints work for manual testing:
  - `https://candle-pattern-monitor.lumbar-heaven.workers.dev/health`
  - `https://candle-pattern-monitor.lumbar-heaven.workers.dev/run`
  - `https://candle-pattern-monitor.lumbar-heaven.workers.dev/price-report`

## 🔧 Your action: Deploy to your own Cloudflare account

### Step 1: Log in to Cloudflare

```bash
cd /home/mondo/candle-pattern-monitor/src-worker
wrangler login
```

This opens a browser — log in to your Cloudflare account.

### Step 2: Set secrets

```bash
# Set your Telegram bot token (the one currently valid)
wrangler secret put TELEGRAM_BOT_TOKEN
# <paste your bot token when prompted>

# Set your Telegram chat ID
wrangler secret put TELEGRAM_CHAT_ID
# <paste: 6580853770>

# Optional: Binance API key (not required, public endpoints work without it)
wrangler secret put BINANCE_API_KEY
```

### Step 3: Deploy

```bash
wrangler deploy
```

### Step 4: Verify cron triggers

After deployment, check the Cloudflare dashboard → Workers → candle-pattern-monitor → Triggers. You should see:
- `*/15 * * * *` — Pattern monitor (every 15 min)
- `5 * * * *` — Price report (hourly at :05)

### Step 5: Test

```bash
# Manual test endpoints
curl https://<your-subdomain>.workers.dev/health
curl https://<your-subdomain>.workers.dev/run
curl https://<your-subdomain>.workers.dev/price-report

# View logs
wrangler tail
```

## Pricing

Cloudflare Workers free tier includes:
- 100,000 requests/day (your cron uses ~96 + 1 = 97 requests/day)
- 10ms CPU time per request (your script uses ~1-2s)
- Cron triggers (up to 5 per worker on free tier)
- ✅ 100% free, no credit card needed
