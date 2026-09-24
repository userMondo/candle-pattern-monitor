import { describe, it, expect } from 'vitest';
import { detectPatterns, formatPatternAlert, formatPriceReport } from '../patterns';
import type { CandleData } from '../types';

function makeCandle(open: number, high: number, low: number, close: number, openTime: number = 100000, closeTime: number = 100060, volume: number = 1000): CandleData {
  return {
    openTime,
    open,
    high,
    low,
    close,
    volume,
    closeTime,
    isClosed: true,
  };
}

describe('Pattern Detection', () => {
  it('detects Bullish Engulfing', () => {
    // Need 3 candles: one older, prev (bearish), latest (bullish engulfing)
    const c0 = makeCandle(90, 95, 88, 92, 0, 50000);
    const c1 = makeCandle(100, 105, 95, 96);  // bearish
    const c2 = makeCandle(96, 110, 94, 109);  // bullish engulfing
    const patterns = detectPatterns([c0, c1, c2]);
    expect(patterns.some(p => p.name === 'Bullish Engulfing')).toBe(true);
    const eng = patterns.find(p => p.name === 'Bullish Engulfing');
    expect(eng?.strength).toBe(2);
  });

  it('detects Doji', () => {
    // Doji: open ≈ close, small body
    const c = makeCandle(100, 102, 98, 100.1);
    const patterns = detectPatterns([makeCandle(100, 105, 95, 96), makeCandle(100, 105, 95, 96), c]);
    expect(patterns.some(p => p.name === 'Doji')).toBe(true);
  });

  it('detects Bullish Pinbar', () => {
    // Long lower wick, small body at top
    const prev = makeCandle(90, 92, 88, 91, 0, 50000);  // older, lower
    const prev2 = makeCandle(91, 93, 89, 92, 0, 100000);
    const c = makeCandle(100, 101, 80, 100.5);  // pinbar
    const patterns = detectPatterns([prev2, prev, c]);
    expect(patterns.some(p => p.name === 'Bullish Pinbar')).toBe(true);
  });

  it('returns empty for insufficient candles', () => {
    const patterns = detectPatterns([makeCandle(100, 105, 95, 96)]);
    expect(patterns).toEqual([]);
  });

  it('filters by focus', () => {
    const c0 = makeCandle(90, 100, 88, 92, 0, 50000);
    const c1 = makeCandle(100, 105, 95, 96);  // bearish
    // Doji: open ≈ close, tiny body relative to range (open=100.0, close=100.1, range=100.0-99.9)
    const c2 = makeCandle(100.0, 100.5, 99.9, 100.1);  // body 0.1, range 0.6 → 0.17 (too high)
    // Real doji: open=100.0, close=100.01, high=100.5, low=99.5 → body=0.01, range=1.0 → 1%
    const doji = makeCandle(100.0, 100.5, 99.5, 100.01);
    const patterns = detectPatterns([c0, c1, doji], 'doji');
    expect(patterns.some(p => p.name === 'Doji')).toBe(true);
    expect(patterns.some(p => p.name === 'Bullish Engulfing')).toBe(false);
  });
});

describe('Alert Formatting', () => {
  it('includes UTC+7 in pattern alert', () => {
    const candle = makeCandle(100, 110, 95, 105, 100000, 960000, 5000);
    const patterns = [{ name: 'Bullish Engulfing', direction: 'bullish' as const, strength: 2, description: 'test' }];
    const alert = formatPatternAlert('BTCUSDT', '15m', patterns, candle, '2024-01-01 12:00:00 UTC+7');
    expect(alert).toContain('UTC+7');
    expect(alert).toContain('67%'); // 2/3 strength
  });

  it('includes percentage strength (3/3 = 100%)', () => {
    const candle = makeCandle(100, 110, 95, 105);
    const patterns = [{ name: 'Morning Star', direction: 'bullish' as const, strength: 3, description: 'test' }];
    const alert = formatPatternAlert('BTCUSDT', '15m', patterns, candle, '');
    expect(alert).toContain('100%');
  });

  it('includes price change percentage', () => {
    const candle = makeCandle(100, 110, 95, 105); // 5% gain
    const patterns = [{ name: 'Bullish Engulfing', direction: 'bullish' as const, strength: 2, description: 'test' }];
    const alert = formatPatternAlert('BTCUSDT', '15m', patterns, candle, '');
    expect(alert).toContain('Change:');
    expect(alert).toContain('%');
  });

  it('includes body and wick percentages', () => {
    const candle = makeCandle(100, 110, 95, 105);
    const patterns = [{ name: 'Bullish Engulfing', direction: 'bullish' as const, strength: 2, description: 'test' }];
    const alert = formatPatternAlert('BTCUSDT', '15m', patterns, candle, '');
    expect(alert).toContain('Body:');
    expect(alert).toContain('Upper Wick:');
    expect(alert).toContain('Lower Wick:');
    expect(alert).toContain('% of range');
  });

  it('includes direction icons', () => {
    const candle = makeCandle(100, 105, 95, 104);
    const patterns = [{ name: 'Bullish Engulfing', direction: 'bullish' as const, strength: 2, description: 'test' }];
    const alert = formatPatternAlert('BTCUSDT', '15m', patterns, candle, '');
    expect(alert).toContain('🟢');
  });

  it('formats price report with all symbols', () => {
    const tickers = [
      { symbol: 'BTCUSDT', price: 83247.94, priceChangePct: -2.95, high24h: 85942.96, low24h: 82891.15, volume: 52.47 },
      { symbol: 'NEARUSDT', price: 4.195, priceChangePct: -8.88, high24h: 4.80, low24h: 4.03, volume: 89217.80 },
    ];
    const report = formatPriceReport(tickers, '2024-01-01 12:00:00 UTC+7');
    expect(report).toContain('Hourly Price Report');
    expect(report).toContain('UTC+7');
    expect(report).toContain('BTCUSDT');
    expect(report).toContain('NEARUSDT');
    expect(report).toContain('-2.95%');
    expect(report).toContain('2 pairs monitored');
  });
});
