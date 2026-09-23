# 🚀 CRITICAL: Add GitHub Secrets to Receive Telegram Alerts

The cron runs are succeeding (exit 0) but no alerts are sent because `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` are **not set as GitHub repository secrets**.

## Step-by-Step Instructions

### Step 1: Open GitHub Repo Settings
1. Go to: https://github.com/userMondo/candle-pattern-monitor
2. Click the **Settings** tab at the top of the repo
3. In the left sidebar, scroll down and click **Secrets and variables** → **Actions**

### Step 2: Add Each Secret
For EACH of the 3 secrets below:

1. Click the green **"New repository secret"** button (top right)
2. Fill in:
   - **Name**: (the secret name)
   - **Secret**: (the value — copy from your local `.env` file)
3. Click **Add secret**
4. Repeat for the next secret

### Step 3: Get Values from Your Local .env
Your local `.env` file has the correct values already configured. To read them:

```bash
cd /home/mondo/candle-pattern-monitor
cat .env
```

You'll see:
```
TELEGRAM_BOT_TOKEN=8800671132:***
TELEGRAM_CHAT_ID=6580853770
BINANCE_API_KEY=HTvhNcdSX04zn3H1ilJv8bTaJSr8AKyn6GFbiZT76rRfNXKYpC82UhYfI0O3XrsE
```

Use these exact values for the corresponding GitHub secrets.

### Step 4: Verify
After adding all 3 secrets, trigger a manual run:
1. Go to: https://github.com/userMondo/candle-pattern-monitor/actions
2. Click **"Candle Pattern Monitor"** workflow
3. Click the **"Run workflow"** dropdown
4. Click **"Run workflow"**
5. Wait ~10 seconds, then click the run to see step logs
6. The "Run candle pattern monitor" step should show pattern detection + "Alert sent: True"

## Why No Alerts Before
- **GitHub PAT** used has `contents: write` and `workflow` scope but **NOT `secrets: write`** — could not set secrets via API
- **Cron empty inputs**: GitHub `schedule` events pass empty strings for `${{ inputs.xxx }}` — FIXED (commit `75e1959`)
- **Missing secrets**: Without `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`, the monitor runs but skips Telegram

## Cron Schedule (all times UTC)
| Schedule | Frequency | UTC | Your Time (UTC+7) |
|----------|-----------|-----|-------------------|
| `*/15 * * * *` | Every 15 min | :00, :15, :30, :45 | Every 15 min (offset +7h) |
| `0 * * * *` | Hourly | :00 each hour | Hourly |
| `0 */4 * * *` | Every 4h | 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 | 07:00, 11:00, 15:00, 19:00, 23:00 |

⚠️ **Note**: GitHub Actions cron fires within a ±15 minute window, not at exact minute marks.
This is a GitHub platform limitation — the cron syntax is correct.
