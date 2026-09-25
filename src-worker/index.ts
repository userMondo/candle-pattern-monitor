/**
 * Candle Pattern Monitor — Cloudflare Workers (TypeScript)
 *
 * 24/7 candlestick pattern monitoring for crypto pairs.
 * Triggers Telegram alerts with enhanced formatting (UTC+7, % strength, candle details).
 * Runs on Cloudflare Workers cron triggers (exact-second precision, free tier).
 */
import { detectPatterns, formatPatternAlert, formatPriceReport, PatternResult } from './patterns';
import { BinanceClient } from './binanceClient';
import { TelegramBot } from './telegramBot';
import type { Env } from './types';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'ok', time: new Date().toISOString() }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname === '/run') {
      const interval = url.searchParams.get('interval') || env.INTERVAL || '15m';
      return await handleManualRun(env, interval);
    }

    if (url.pathname === '/price-report') {
      return await handlePriceReport(env);
    }

    return new Response('Candle Pattern Monitor — use /run or /health', { status: 200 });
  },

  // Cron handler — triggered every 15 minutes by Cloudflare's scheduler
  // Inside this handler, we determine which intervals to check based on current time:
  //   - Every 15m tick: always check 15m patterns
  //   - At :05 of every hour: also send hourly price report
  //   - At :20 of every hour: also check 1h patterns
  //   - At :35 (only at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC): check 4h patterns
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    const now = new Date();
    const minute = now.getUTCMinutes();
    const hour = now.getUTCHours();
    const logMessages: string[] = [];

    // Always: 15m pattern check
    const result15m = await handleManualRun(env, '15m');
    const body15m = await result15m.clone().text();
    const data15m = JSON.parse(body15m);
    logMessages.push(`15m: ${data15m.alertsSent} alerts`);

    // Price report at :05 of every hour
    if (minute === 0 || minute === 15 || minute === 30 || minute === 45) {
      // Run price report at every 15m tick (staggered, but always runs)
      // Actually, only at :05 — but since we run at :00/:15/:30/:45, let's use :00
      if (minute === 0) {
        const resultPrice = await handlePriceReport(env);
        const bodyPrice = await resultPrice.clone().text();
        logMessages.push(`price-report: ${bodyPrice.substring(0, 100)}`);
      }
    }

    // 1h pattern check at :20 (closest to */15 that makes sense)
    if (minute === 15) {
      const result1h = await handleManualRun(env, '1h');
      const body1h = await result1h.clone().text();
      const data1h = JSON.parse(body1h);
      logMessages.push(`1h: ${data1h.alertsSent} alerts`);
    }

    // 4h pattern check at :30, only at 00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC
    if (minute === 30 && hour % 4 === 0) {
      const result4h = await handleManualRun(env, '4h');
      const body4h = await result4h.clone().text();
      const data4h = JSON.parse(body4h);
      logMessages.push(`4h: ${data4h.alertsSent} alerts`);
    }

    console.log(`[cron] ${now.toISOString()} → ${logMessages.join(' | ')}`);
  },
};

async function handleManualRun(env: Env, interval: string = '15m'): Promise<Response> {
  const symbols = (env.WATCHLIST_SYMBOLS || 'BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT')
    .split(',').map(s => s.trim()).filter(Boolean);
  const focus = env.PATTERN_FOCUS || '';

  const binance = new BinanceClient(env.BINANCE_API_KEY);
  const bot = new TelegramBot(env.TELEGRAM_BOT_TOKEN, env.TELEGRAM_CHAT_ID);

  let alertsSent = 0;
  const results: Array<{ symbol: string; interval: string; patterns: PatternResult[]; sent: boolean }> = [];

  for (const symbol of symbols) {
    try {
      const candles = await binance.getKlines(symbol, interval, 50);
      if (!candles || candles.length < 3) continue;

      // Filter to closed candles only
      const closed = candles.filter(c => c.isClosed);
      if (closed.length < 3) continue;

      const patterns = detectPatterns(closed, focus);
      if (patterns.length === 0) continue;

      const latest = closed[closed.length - 1];
      const alert = formatPatternAlert(symbol, interval, patterns, latest);
      const sent = await bot.sendMessage(alert);

      results.push({ symbol, interval, patterns, sent });
      if (sent) alertsSent++;
    } catch (e) {
      console.error(`Error checking ${symbol}:`, e);
    }
  }

  const body = JSON.stringify({
    status: 'ok',
    symbols,
    interval,
    alertsSent,
    results,
  });

  return new Response(body, { headers: { 'Content-Type': 'application/json' } });
}

async function handlePriceReport(env: Env): Promise<Response> {
  const symbols = (env.WATCHLIST_SYMBOLS || 'BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT')
    .split(',').map(s => s.trim()).filter(Boolean);

  const binance = new BinanceClient(env.BINANCE_API_KEY);
  const bot = new TelegramBot(env.TELEGRAM_BOT_TOKEN, env.TELEGRAM_CHAT_ID);

  const tickers: Array<{ symbol: string; price: number; priceChangePct: number; high24h: number; low24h: number; volume: number }> = [];

  for (const symbol of symbols) {
    try {
      const t = await binance.getPriceTicker(symbol);
      if (t) tickers.push(t);
    } catch (e) {
      console.error(`Error fetching ticker ${symbol}:`, e);
    }
  }

  if (tickers.length === 0) {
    return new Response(JSON.stringify({ error: 'No tickers retrieved' }), { status: 500 });
  }

  const report = formatPriceReport(tickers);
  const sent = await bot.sendMessage(report);

  return new Response(JSON.stringify({ status: 'ok', sent, tickers: tickers.length }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
