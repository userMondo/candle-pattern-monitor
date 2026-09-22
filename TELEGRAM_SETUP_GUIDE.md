# Telegram + GitHub Setup Guide

When you return, follow these steps to activate Telegram alerts:

## Step 1: Add Telegram secrets to GitHub

1. Go to https://github.com/userMondo/candle-pattern-monitor/settings/secrets/actions
2. Add two repository secrets:
   - **TELEGRAM_BOT_TOKEN** = `<your_telegram_bot_token>` *(from @BotFather)*
   - **TELEGRAM_CHAT_ID** = (run the step below to find it)

## Step 2: Get your Telegram chat ID

1. Open Telegram, search for `@jiodsjfiebot`
2. Send `/start`
3. Run: `python3 src/get_chat_id.py --token <your_token>`
4. Copy the resulting chat ID into the GitHub secret above

## Step 3: (Optional) Add Binance API key

1. Add **BINANCE_API_KEY** = `<your_binance_api_key>`
2. This is optional — the Binance public klines endpoint works without it, but the key increases rate limits

## Verification

After adding secrets, the GitHub Actions cron will automatically start sending alerts. You can also test manually:

1. Go to https://github.com/userMondo/candle-pattern-monitor/actions
2. Click "Candle Pattern Monitor"
3. Click "Run workflow" → "Run workflow_dispatch"
4. Adjust parameters if needed (default: 15m interval, all patterns)
5. Click "Run workflow"
6. Check the "Run candle pattern monitor" step output for any alerts

## What the bot looks for

- **All 13+ pattern types**: Engulfing, Doji, Doji+Engulfing, Hammer, Hanging Man, Shooting Star, Inverted Hammer, Bull/Bear Pinbar, Morning Star, Evening Star
- Use `--focus` to limit to specific categories

## Default watchlist

`BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT` (PAXG = gold-backed token)

## Cron schedule (runs in UTC)

- Every 15 minutes (`*/15 * * * *`) — all patterns on 15m interval
- Every hour (`0 * * * *`) — all patterns on 1h interval
- Every 4 hours (`0 */4 * * *`) — all patterns on 4h interval
