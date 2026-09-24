/**
 * Type definitions for Candle Pattern Monitor
 */
export interface Env {
  TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_CHAT_ID: string;
  BINANCE_API_KEY?: string;
  WATCHLIST_SYMBOLS?: string;
  INTERVAL?: string;
  PATTERN_FOCUS?: string;
}

export interface CandleData {
  openTime: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  closeTime: number;
  isClosed: boolean;
}

export interface Kline {
  openTime: number;
  open: string;
  high: string;
  low: string;
  close: string;
  volume: string;
  closeTime: number;
  isClosed: boolean;
}

// PriceTicker interface (moved from patterns.ts for shared types)
export interface PriceTicker {
  symbol: string;
  price: number;
  priceChangePct: number;
  high24h: number;
  low24h: number;
  volume: number;
}
