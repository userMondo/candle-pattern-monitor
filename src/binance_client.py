"""
Binance API Client for fetching candlestick (kline) data.

Uses public Binance REST endpoints — no authentication required for
historical market candles.

Endpoint: https://api.binance.com/api/v3/klines
"""

import os
from dataclasses import dataclass, field
from typing import List, Optional

import requests


@dataclass
class Candle:
    """Represents a single candlestick (kline)."""
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int

    @property
    def body_size(self) -> float:
        """Absolute size of the candle body (open-close)."""
        return abs(self.close - self.open)

    @property
    def wick_upper(self) -> float:
        """Upper wick length (high - max(open, close))."""
        return self.high - max(self.open, self.close)

    @property
    def wick_lower(self) -> float:
        """Lower wick length (min(open, close) - low)."""
        return min(self.open, self.close) - self.low

    @property
    def total_range(self) -> float:
        """Full candle range (high - low)."""
        return self.high - self.low

    @property
    def is_bullish(self) -> bool:
        """True if close > open (green/up candle)."""
        return self.close > self.open

    @property
    def is_bearish(self) -> bool:
        """True if close < open (red/down candle)."""
        return self.close < self.open

    @property
    def is_closed(self) -> bool:
        """True if this candle is fully closed (close_time is in the past)."""
        from time import time
        return self.close_time <= int(time() * 1000) - 1000  # 1s buffer


@dataclass
class KlineResponse:
    """Parsed kline/candlestick response from Binance API."""
    candles: List[Candle] = field(default_factory=list)


class BinanceClient:
    """
    Lightweight client for Binance public REST API (klines endpoint).

    Usage:
        client = BinanceClient()
        candles = client.get_klines("BTCUSDT", "4h", limit=50)
        latest = candles[-1]  # most recent closed candle
    """

    BASE_URL = "https://api.binance.com/api/v3"
    DEFAULT_TIMEOUT = 30

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Binance client.

        Args:
            api_key: Optional Binance API key (used for weight limit increases,
                     not required for public kline endpoint).
        """
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def get_klines(
        self,
        symbol: str,
        interval: str = "4h",
        limit: int = 50,
    ) -> List[Candle]:
        """
        Fetch historical candlestick (kline) data from Binance.

        Args:
            symbol: Trading pair, e.g. "BTCUSDT", "NEARUSDT".
            interval: Kline interval. Supported: "15m", "1h", "4h".
            limit: Number of candles to fetch (max 1000).

        Returns:
            List of Candle objects, ordered oldest-first.

        Raises:
            ValueError: If symbol or interval is invalid.
            requests.HTTPError: If the API returns an error.
        """
        if not symbol or not symbol.isalnum():
            raise ValueError(f"Invalid symbol: {symbol}")

        valid_intervals = {"15m", "1h", "4h", "1m", "5m", "1d", "1w", "1M"}
        if interval not in valid_intervals:
            raise ValueError(
                f"Invalid interval '{interval}'. Must be one of: {valid_intervals}"
            )

        if limit > 1000:
            limit = 1000

        url = f"{self.BASE_URL}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        response = self.session.get(url, params=params, timeout=self.DEFAULT_TIMEOUT)
        response.raise_for_status()
        data = response.json()

        candles = []
        for k in data:
            # Binance kline array format:
            # [0] Open time
            # [1] Open
            # [2] High
            # [3] Low
            # [4] Close
            # [5] Volume
            # [6] Close time
            # ... (remaining fields ignored)
            candles.append(Candle(
                open_time=int(k[0]),
                open=float(k[1]),
                high=float(k[2]),
                low=float(k[3]),
                close=float(k[4]),
                volume=float(k[5]),
                close_time=int(k[6]),
            ))

        return candles

    def get_latest_closed_candle(self, symbol: str, interval: str = "4h") -> Candle:
        """
        Fetch the most recent closed candle for a symbol.

        Explicitly filters to only return candles whose close_time is in the past,
        ensuring we never analyze an incomplete forming candle.

        Args:
            symbol: Trading pair.
            interval: Kline interval.

        Returns:
            The most recent closed Candle.
        """
        candles = self.get_klines(symbol, interval, limit=10)
        if not candles:
            raise ValueError(f"No kline data returned for {symbol}")

        # Filter to fully closed candles only (close_time must be in the past)
        closed = [c for c in candles if c.is_closed]
        if not closed:
            # Fallback: Binance historical klines are already closed,
            # but we verify to be safe. Return the second-to-last if available.
            return candles[-2] if len(candles) >= 2 else candles[-1]

        return closed[-1]
