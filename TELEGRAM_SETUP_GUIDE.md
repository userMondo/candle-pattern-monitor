# Telegram + GitHub Setup Guide

When you return, follow these steps to activate Telegram alerts:

## Step 1: Add Telegram secrets to GitHub

1. Go to https://github.com/userMondo/candle-pattern-monitor/settings/secrets/actions
2. Add two repository secrets:
   - **TELEGRAM_BOT_TOKEN** = `8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY`
   - **TELEGRAM_CHAT_ID** = (run the step below to find it)

## Step 2: Get your Telegram chat ID

1. Open Telegram, search for `@jiodsjfiebot`
2. Send `/start`
3. Run: `python3 src/get_chat_id.py --token 8800671132:AAHQnXSnhOJ3HVkZje-G9unj9OyG_XsZwuY`
4. Copy the resulting chat ID into the GitHub secret above

## Step 3: (Optional) Add Binance API key

1. Add **BINANCE_API_KEY** = `HTvhNcdSX04zn3H1ilJv8bTaJSr8AKyn6GFbiZT76rRfNXKYpC82UhYfI0O3XrsE`
2. This is optional — the Binance public klines endpoint works without it, but the key increases rate limits

## Verification

After adding secrets, the GitHub Actions cron will automatically start sending alerts. You can also test manually:

1. Go to https://github.com/userMondo/candle-pattern-monitor/actions
2. Click "Candle Pattern Monitor"
3. Click "Run workflow" → "Run workflow_dispatch"
4. Adjust parameters if needed (default: 15m interval, engulfing+doji focus)
5. Click "Run workflow"
6. Check the "Run candle pattern monitor" step output for any alerts

## What the bot looks for

- **Engulfing**: Bullish/Bearish Engulfing candles
- **Doji**: Open ≈ Close (market indecision)
- **Doji + Engulfing**: Doji followed by a strong reversal candle (3/3 strength)

## Default watchlist

`BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` (PAXG = gold-backed token)

## Cron schedule

- Every 15 minutes (`*/15 * * * *`) — primary patterns (Engulfing + Doji)
- Every hour (`0 * * * *`) — full pattern scan
- Every 4 hours (`0 */4 * * *`) — full pattern scan
