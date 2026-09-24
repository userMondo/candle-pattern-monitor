/**
 * Candle pattern detection and alert formatting.
 * Ported from Python src/patterns.py to TypeScript.
 *
 * Patterns: Engulfing, Doji, Doji+Engulfing, Hammer, Hanging Man,
 * Shooting Star, Inverted Hammer, Bull/Bear Pinbar, Morning Star, Evening Star.
 * Plus enhanced alert formatting with UTC+7, % strength, candle details.
 */
import type { CandleData, PriceTicker } from './types';

export interface PatternResult {
  name: string;
  direction: 'bullish' | 'bearish' | 'neutral';
  strength: number; // 1-3
  description: string;
}

/**
 * Detect all patterns (or filtered subset) for the latest closed candle.
 * @param candles  Array of CandleData (oldest → newest). Latest closed candle = candles[-1].
 * @param focus    Comma-separated pattern categories to filter (empty string = ALL).
 */
export function detectPatterns(candles: CandleData[], focus?: string): PatternResult[] {
  if (candles.length < 3) return [];

  const latest = candles[candles.length - 1];
  const prev = candles[candles.length - 2];
  const prev2 = candles[candles.length - 3];

  // Filter categories
  let focusSet: Set<string> | null = null;
  if (focus && focus.trim()) {
    focusSet = new Set(focus.split(',').map(f => f.trim()).filter(Boolean).map(f => f.toLowerCase()));
  }

  function inFocus(category: string): boolean {
    return focusSet === null || focusSet.has(category);
  }

  const patterns: PatternResult[] = [];

  // ── Engulfing ──────────────────────────────────────────────
  if (inFocus('engulfing')) {
    const eng = detectEngulfing(latest, prev);
    if (eng) patterns.push(eng);
  }

  // ── Doji ───────────────────────────────────────────────────
  if (inFocus('doji')) {
    const doji = detectDoji(latest);
    if (doji) patterns.push(doji);
  }

  // ── Doji + Engulfing (highest priority, 3/3 strength) ──────
  if (inFocus('engulfing')) {
    const dojiEng = detectDojiEngulfing(latest, prev, prev2);
    if (dojiEng) patterns.push(dojiEng);
  }

  // ── Pinbar ─────────────────────────────────────────────────
  if (inFocus('pinbar')) {
    const pinbar = detectPinbar(latest, prev);
    if (pinbar) patterns.push(pinbar);
  }

  // ── Hammer / Hanging Man ────────────────────────────────────
  if (inFocus('hammer')) {
    const hammer = detectHammer(latest, prev, prev2);
    if (hammer) patterns.push(hammer);
  }

  // ── Shooting Star / Inverted Hammer ────────────────────────
  if (inFocus('shooting_star')) {
    const star = detectShootingStar(latest, prev, prev2);
    if (star) patterns.push(star);
  }

  // ── Morning Star ───────────────────────────────────────────
  if (inFocus('morning_star')) {
    const ms = detectMorningStar(latest, prev, prev2);
    if (ms) patterns.push(ms);
  }

  // ── Evening Star ───────────────────────────────────────────
  if (inFocus('evening_star')) {
    const es = detectEveningStar(latest, prev, prev2);
    if (es) patterns.push(es);
  }

  return patterns;
}

// ── Candle helper functions ───────────────────────────────────

function body(c: CandleData): number {
  return Math.abs(c.close - c.open);
}

function wickUp(c: CandleData): number {
  return c.high - Math.max(c.open, c.close);
}

function wickDown(c: CandleData): number {
  return Math.min(c.open, c.close) - c.low;
}

function range(c: CandleData): number {
  return c.high - c.low;
}

function isBullish(c: CandleData): boolean {
  return c.close > c.open;
}

function isBearish(c: CandleData): boolean {
  return c.close < c.open;
}

// ── Pattern detectors ─────────────────────────────────────────

function detectEngulfing(latest: CandleData, prev: CandleData): PatternResult | null {
  // Bullish engulfing: bullish candle engulfs bearish candle
  if (isBullish(latest) && isBearish(prev)) {
    const bodyLatest = body(latest);
    const bodyPrev = body(prev);
    if (bodyLatest > bodyPrev && latest.open <= prev.close && latest.close >= prev.open) {
      return {
        name: 'Bullish Engulfing',
        direction: 'bullish',
        strength: 2,
        description: 'Large bullish candle fully engulfs previous bearish candle — potential bullish reversal.',
      };
    }
  }

  // Bearish engulfing: bearish candle engulfs bullish candle
  if (isBearish(latest) && isBullish(prev)) {
    const bodyLatest = body(latest);
    const bodyPrev = body(prev);
    if (bodyLatest > bodyPrev && latest.open >= prev.close && latest.close <= prev.open) {
      return {
        name: 'Bearish Engulfing',
        direction: 'bearish',
        strength: 2,
        description: 'Large bearish candle fully engulfs previous bullish candle — potential bearish reversal.',
      };
    }
  }

  return null;
}

function detectDoji(c: CandleData): PatternResult | null {
  const rng = range(c);
  if (rng === 0) return null;
  const bodySize = body(c);
  if (bodySize / rng <= 0.05) {
    return {
      name: 'Doji',
      direction: 'neutral',
      strength: 1,
      description: 'Open and close nearly equal — market indecision, potential reversal signal.',
    };
  }
  return null;
}

function detectDojiEngulfing(latest: CandleData, prev: CandleData, prev2: CandleData): PatternResult | null {
  // Look for doji on prev2, then engulfing on latest
  const dojiOnPrev2 = detectDoji(prev2);
  if (!dojiOnPrev2) return null;

  // Doji after downtrend + bullish engulfing = Doji + Bullish Engulfing
  if (isBullish(latest) && isBearish(prev) && dojiOnPrev2) {
    const eng = detectEngulfing(latest, prev);
    if (eng && eng.name === 'Bullish Engulfing') {
      return {
        name: 'Doji + Bullish Engulfing',
        direction: 'bullish',
        strength: 3,
        description: 'Doji after downtrend followed by strong bullish engulfing — high-confidence bullish reversal (3/3).',
      };
    }
  }

  // Doji after uptrend + bearish engulfing = Doji + Bearish Engulfing
  if (isBearish(latest) && isBullish(prev) && dojiOnPrev2) {
    const eng = detectEngulfing(latest, prev);
    if (eng && eng.name === 'Bearish Engulfing') {
      return {
        name: 'Doji + Bearish Engulfing',
        direction: 'bearish',
        strength: 3,
        description: 'Doji after uptrend followed by strong bearish engulfing — high-confidence bearish reversal (3/3).',
      };
    }
  }

  return null;
}

function detectPinbar(latest: CandleData, prev: CandleData): PatternResult | null {
  const rng = range(latest);
  if (rng === 0) return null;
  const bodyLatest = body(latest);
  const upWick = wickUp(latest);
  const downWick = wickDown(latest);
  const bodyRatio = bodyLatest / rng;
  const upRatio = upWick / rng;
  const downRatio = downWick / rng;

  // Bullish pinbar: long lower wick, small body at top, body in bottom 1/3
  if (downRatio > 0.5 && bodyRatio < 0.3 && upRatio < 0.2) {
    const isReversal = latest.close > prev.close && downWick > bodyLatest * 1.5;
    if (isReversal) {
      return {
        name: 'Bullish Pinbar',
        direction: 'bullish',
        strength: 3,
        description: 'Long lower wick penetrating below previous low with small body at top — strong bullish reversal signal.',
      };
    }
  }

  // Bearish pinbar: long upper wick, small body at bottom, body in top 1/3
  if (upRatio > 0.5 && bodyRatio < 0.3 && downRatio < 0.2) {
    const isReversal = latest.close < prev.close && upWick > bodyLatest * 1.5;
    if (isReversal) {
      return {
        name: 'Bearish Pinbar',
        direction: 'bearish',
        strength: 3,
        description: 'Long upper wick penetrating above previous high with small body at bottom — strong bearish reversal signal.',
      };
    }
  }

  return null;
}

function detectHammer(latest: CandleData, prev: CandleData, prev2: CandleData): PatternResult | null {
  const rng = range(latest);
  if (rng === 0) return null;
  const bodyLatest = body(latest);
  const bodyRatio = bodyLatest / rng;
  const downRatio = wickDown(latest) / rng;
  const upRatio = wickUp(latest) / rng;

  // Hammer: long lower wick (2x+ body), small body at top
  if (downRatio >= 0.5 && bodyRatio <= 0.3 && downRatio >= bodyLatest * 2) {
    // Determine direction based on position
    const bodyTop = Math.max(latest.open, latest.close);
    const bodyBottom = Math.min(latest.open, latest.close);

    if (bodyTop > (latest.high + latest.low) / 2) {
      // Body at top → Hanging Man (bearish)
      if (isBullish(prev) && isBullish(prev2)) {
        return {
          name: 'Hanging Man',
          direction: 'bearish',
          strength: 2,
          description: 'Hammer pattern appearing after uptrend — potential bearish reversal.',
        };
      }
    } else if (bodyBottom < (latest.high + latest.low) / 2) {
      // Body at top, small body at top → Hammer (bullish)
      if (isBearish(prev) && isBearish(prev2)) {
        return {
          name: 'Hammer',
          direction: 'bullish',
          strength: 2,
          description: 'Small body at top of candle with long lower wick (2x+) — potential bullish reversal at support.',
        };
      }
    }
  }

  return null;
}

function detectShootingStar(latest: CandleData, prev: CandleData, prev2: CandleData): PatternResult | null {
  const rng = range(latest);
  if (rng === 0) return null;
  const bodyLatest = body(latest);
  const bodyRatio = bodyLatest / rng;
  const upRatio = wickUp(latest) / rng;
  const downRatio = wickDown(latest) / rng;

  // Shooting star: long upper wick, small body at bottom
  if (upRatio >= 0.5 && bodyRatio <= 0.3 && upRatio >= bodyLatest * 2) {
    const bodyBottom = Math.min(latest.open, latest.close);

    if (bodyBottom > (latest.high + latest.low) / 2) {
      // Body at bottom → Shooting Star (bearish)
      if (isBullish(prev) && isBullish(prev2)) {
        return {
          name: 'Shooting Star',
          direction: 'bearish',
          strength: 2,
          description: 'Small body at bottom with long upper wick — potential bearish reversal at resistance.',
        };
      }
    } else if (bodyBottom < (latest.high + latest.low) / 2) {
      // Body at top → Inverted Hammer (bullish)
      if (isBearish(prev) && isBearish(prev2)) {
        return {
          name: 'Inverted Hammer',
          direction: 'bullish',
          strength: 2,
          description: 'Shooting star pattern appearing after downtrend — potential bullish reversal.',
        };
      }
    }
  }

  return null;
}

function detectMorningStar(latest: CandleData, prev: CandleData, prev2: CandleData): PatternResult | null {
  // 3-candle bullish reversal: large bearish, small bullish/gap down, large bullish closing above midpoint of first
  if (!isBearish(prev2) || !isBullish(latest)) return null;

  const body2 = body(prev2);
  const bodyLatest = body(latest);

  // First candle (prev2): large bearish
  if (body2 < range(prev2) * 0.5) return null;

  // Second candle (prev): small body, gaps down
  const bodyPrev = body(prev);
  const rngPrev = range(prev);
  if (rngPrev === 0) return null;
  if (bodyPrev / rngPrev > 0.3) return null; // body too large (should be small/star/doji-like)

  // Gap down: prev's high < prev2's low
  if (prev.high >= prev2.low) return null;

  // Third candle (latest): large bullish, closes above midpoint of prev2
  if (bodyLatest < body2 * 0.5) return null;
  const midpoint2 = (prev2.open + prev2.close) / 2;
  if (latest.close <= midpoint2) return null;

  return {
    name: 'Morning Star',
    direction: 'bullish',
    strength: 3,
    description: '3-candle bullish reversal: large red, small gap down, large green closing above midpoint of first candle.',
  };
}

function detectEveningStar(latest: CandleData, prev: CandleData, prev2: CandleData): PatternResult | null {
  // 3-candle bearish reversal: large bullish, small bearish/gap up, large bearish closing below midpoint of first
  if (!isBullish(prev2) || !isBearish(latest)) return null;

  const body2 = body(prev2);
  const bodyLatest = body(latest);

  // First candle (prev2): large bullish
  if (body2 < range(prev2) * 0.5) return null;

  // Second candle (prev): small body, gaps up
  const bodyPrev = body(prev);
  const rngPrev = range(prev);
  if (rngPrev === 0) return null;
  if (bodyPrev / rngPrev > 0.3) return null;

  // Gap up: prev's low > prev2's high
  if (prev.low <= prev2.high) return null;

  // Third candle (latest): large bearish, closes below midpoint of prev2
  if (bodyLatest < body2 * 0.5) return null;
  const midpoint2 = (prev2.open + prev2.close) / 2;
  if (latest.close >= midpoint2) return null;

  return {
    name: 'Evening Star',
    direction: 'bearish',
    strength: 3,
    description: '3-candle bearish reversal: large green, small gap up, large red closing below midpoint of first candle.',
  };
}

// ── Alert formatters ───────────────────────────────────────────

function pctChange(open: number, close: number): number {
  if (open === 0) return 0;
  return ((close - open) / open) * 100;
}

function formatNumber(n: number, decimals: number = 2): string {
  return n.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
}

function directionIcon(direction: string): string {
  switch (direction) {
    case 'bullish': return '🟢';
    case 'bearish': return '🔴';
    default: return '⚪';
  }
}

export function formatPatternAlert(
  symbol: string,
  timeframe: string,
  patterns: PatternResult[],
  candle: CandleData,
  timestamp: string = '',
): string {
  const lines: string[] = [];
  lines.push('🕯️ *Candle Pattern Alert*');
  lines.push('');
  lines.push(`*Symbol:* \`${symbol}\``);
  lines.push(`*Timeframe:* \`${timeframe}\``);
  if (timestamp) {
    lines.push(`*Time (UTC+7):* \`${timestamp}\``);
  }
  lines.push('');

  // Candle details
  const rng = range(candle);
  const bodySize = body(candle);
  const upWick = wickUp(candle);
  const downWick = wickDown(candle);
  const change = pctChange(candle.open, candle.close);
  const dir = change > 0 ? 'Bullish' : change < 0 ? 'Bearish' : 'Neutral';

  lines.push('*📊 Candle Details:*');
  lines.push(`  • Open: \`${formatNumber(candle.open, 4)}\``);
  lines.push(`  • Close: \`${formatNumber(candle.close, 4)}\``);
  lines.push(`  • High: \`${formatNumber(candle.high, 4)}\``);
  lines.push(`  • Low: \`${formatNumber(candle.low, 4)}\``);
  lines.push(`  • Body: \`${formatNumber(bodySize, 4)}\` (${rng > 0 ? (bodySize / rng * 100).toFixed(1) : '0'}% of range)`);
  lines.push(`  • Upper Wick: \`${formatNumber(upWick, 4)}\` (${rng > 0 ? (upWick / rng * 100).toFixed(1) : '0'}% of range)`);
  lines.push(`  • Lower Wick: \`${formatNumber(downWick, 4)}\` (${rng > 0 ? (downWick / rng * 100).toFixed(1) : '0'}% of range)`);
  lines.push(`  • Total Range: \`${formatNumber(rng, 4)}\``);
  lines.push(`  • Change: ${change.toFixed(2)}% (${dir})`);
  lines.push('');

  // Pattern details
  for (const p of patterns) {
    const pctStrength = Math.round((p.strength / 3) * 100);
    lines.push(`*Pattern:* \`${p.name}\` ${directionIcon(p.direction)} *Strength:* \`${pctStrength}%\` (${p.strength}/3)`);
    lines.push(p.description);
    lines.push('');
  }

  lines.push('_Alert generated automatically by Candle Pattern Monitor_');
  return lines.join('\n');
}

export function formatPriceReport(tickers: PriceTicker[], timestamp: string = ''): string {
  const lines: string[] = [];
  lines.push('📈 *Hourly Price Report*');
  lines.push('');
  if (timestamp) {
    lines.push(`*Time (UTC+7):* \`${timestamp}\``);
  }
  lines.push('');
  lines.push('_Pair                  Price      24h Δ                        Range          Vol_');

  for (const t of tickers) {
    const icon = t.priceChangePct >= 0 ? '🟢' : '🔴';
    const pct = t.priceChangePct.toFixed(2);
    const price = formatNumber(t.price, 2);
    const high = formatNumber(t.high24h, 2);
    const low = formatNumber(t.low24h, 2);
    const vol = t.volume >= 1000 ? (t.volume / 1000).toFixed(2) + 'K' : t.volume.toFixed(2);

    lines.push(
      `\`${t.symbol.padEnd(12)} ${price} ${icon}${pct}% H: ${high} L: ${low} V: ${vol}\``
    );
  }

  lines.push('');
  lines.push(`_Summary: ${tickers.length} pairs monitored_`);
  lines.push('_Report generated by Candle Pattern Monitor_');
  return lines.join('\n');
}
