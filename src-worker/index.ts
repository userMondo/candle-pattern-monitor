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
import type { Env, CandleData } from './types';

export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);

    if (url.pathname === '/health') {
      return new Response(JSON.stringify({ status: 'ok', time: new Date().toISOString() }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }

    if (url.pathname === '/run') {
      return await handleManualRun(env);
    }

    if (url.pathname === '/price-report') {
      return await handlePriceReport(env);
    }

    return new Response('Candle Pattern Monitor — use /run or /health', { status: 200 });
  },

  // Cron handler — triggered by Cloudflare's scheduler
  // CRON: */15 * * * * for patterns, 5 * * * * for price reports
  async scheduled(event: ScheduledEvent, env: Env, ctx: ExecutionContext): Promise<void> {
    const now = new Date();
    const minute = now.getUTCMinutes();

    // Run price report at :05 of every hour
    if (minute === 5) {
      ctx.wait(await handlePriceReport(env));
    } else {
      // Pattern monitoring on all other cron ticks
      ctx.wait(await handleManualRun(env));
    }
  },
};

async function handleManualRun(env: Env): Promise<Response> {
  const symbols = (env.WATCHLIST_SYMBOLS || 'BTCUSDT,NEARUSDT,ZECUSDT,PAXGUSDT')
    .split(',').map(s => s.trim()).filter(Boolean);
  const interval = env.INTERVAL || '15m';
  const focus = env.PATTERN_FOCUS || '';

  const binance = new BinanceClient(env.BINANCE_API_KEY);
  const bot = new TelegramBot(env.TELEGRAM_BOT_TOKEN, env.TELEGRAM_CHAT_ID);

  let alertsSent = 0;
  const results: Array<{ symbol: string; patterns: PatternResult[]; sent: boolean }> = [];

  for (const symbol of symbols) {
    try {
      const candles = await binance.getKlines(symbol, interval, 50);
      if (!candles || candles.length < 3) continue;

      const closed = candles.filter(c => c.isClosed);
      if (closed.length < 3) continue;

      const patterns = detectPatterns(closed, focus);
      if (patterns.length === 0) continue;

      const latest = closed[closed.length - 1];
      const alert = formatPatternAlert(symbol, interval, patterns, latest);
      const sent = await bot.sendMessage(alert);

      results.push({ symbol, patterns, sent });
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
