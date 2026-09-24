/**
 * Binance API client for Cloudflare Workers.
 * Uses fetch API (available in Workers runtime).
 * Implements endpoint fallback for resilience (api.binance.com + api.binance.us).
 */
import type { CandleData, Kline } from './types';

export class BinanceClient {
  private readonly BASE_URLS = [
    'https://api.binance.com',
    'https://api.binance.us',
  ];
  private readonly apiKey?: string;

  constructor(apiKey?: string) {
    this.apiKey = apiKey;
  }

  private async fetchWithFallback(path: string): Promise<any> {
    const headers: Record<string, string> = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    };
    if (this.apiKey) {
      headers['X-MBX-APIKEY'] = this.apiKey;
    }

    for (const base of this.BASE_URLS) {
      try {
        const url = `${base}${path}`;
        const resp = await fetch(url, { headers });
        if (!resp.ok) {
          // Try next endpoint on HTTP errors (403, 451, 429, etc.)
          if (resp.status === 403 || resp.status === 451 || resp.status === 429) continue;
          throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
        }
        return await resp.json();
      } catch (e) {
        // Try next endpoint on network errors
        const msg = e instanceof Error ? e.message : String(e);
        if (msg.includes('fetch') || msg.includes('HTTP 40') || msg.includes('HTTP 45')) continue;
        throw e;
      }
    }
    throw new Error('All Binance endpoints failed');
  }

  async getKlines(symbol: string, interval: string, limit: number = 50): Promise<CandleData[]> {
    const path = `/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
    const data = await this.fetchWithFallback(path);

    // Binance: [0]=openTime, [1]=open, [2]=high, [3]=low, [4]=close, [5]=volume, [6]=closeTime
    // isClosed: closeTime < current server time. We approximate using closeTime vs now.
    const now = Date.now();
    return data.map((k: any[]) => ({
      openTime: k[0],
      open: parseFloat(k[1]),
      high: parseFloat(k[2]),
      low: parseFloat(k[3]),
      close: parseFloat(k[4]),
      volume: parseFloat(k[5]),
      closeTime: k[6],
      isClosed: k[6] < now - 1000, // 1s buffer for closed candles
    }));
  }

  async getPriceTicker(symbol: string): Promise<{ symbol: string; price: number; priceChangePct: number; high24h: number; low24h: number; volume: number } | null> {
    const data = await this.fetchWithFallback(`/api/v3/ticker/24hr?symbol=${symbol}`);
    return {
      symbol: data.symbol,
      price: parseFloat(data.lastPrice),
      priceChangePct: parseFloat(data.priceChangePercent),
      high24h: parseFloat(data.highPrice),
      low24h: parseFloat(data.lowPrice),
      volume: parseFloat(data.volume),
    };
  }
}
