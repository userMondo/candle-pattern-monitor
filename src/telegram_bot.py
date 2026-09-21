"""
Telegram Bot API client for sending candlestick pattern alerts.

Endpoint: https://api.telegram.org/bot{token}/sendMessage
"""

import os
from typing import Optional

import requests


class TelegramBot:
    """
    Client for sending notifications via Telegram Bot API.

    Usage:
        bot = TelegramBot(token="your_bot_token", chat_id="your_chat_id")
        bot.send_message("BTCUSDT pattern detected: Engulfing")
    """

    BASE_URL = "https://api.telegram.org/bot"

    def __init__(
        self,
        token: Optional[str] = None,
        chat_id: Optional[str] = None,
    ):
        """
        Initialize the Telegram bot.

        Args:
            token: Telegram bot token. Falls back to TELEGRAM_BOT_TOKEN env var.
            chat_id: Telegram chat ID. Falls back to TELEGRAM_CHAT_ID env var.

        Raises:
            ValueError: If token or chat_id is not provided.
        """
        self.token = token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")

        if not self.token:
            raise ValueError(
                "Telegram bot token not provided. Set TELEGRAM_BOT_TOKEN env var "
                "or pass token parameter."
            )
        if not self.chat_id:
            raise ValueError(
                "Telegram chat ID not provided. Set TELEGRAM_CHAT_ID env var "
                "or pass chat_id parameter."
            )

        self.url = f"{self.BASE_URL}{self.token}/sendMessage"

    def send_message(
        self,
        text: str,
        parse_mode: str = "Markdown",
    ) -> bool:
        """
        Send a text message to the configured Telegram chat.

        Args:
            text: Message text (can include Markdown formatting).
            parse_mode: "Markdown", "MarkdownV2", or "HTML". Defaults to "Markdown".

        Returns:
            True if the message was sent successfully, False otherwise.
        """
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": True,
        }

        try:
            response = requests.post(self.url, data=payload, timeout=30)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"[TelegramBot] Failed to send message: {e}")
            return False

    def send_candle_alert(
        self,
        symbol: str,
        interval: str,
        pattern_name: str,
        close_price: float,
        open_price: float,
        high: float,
        low: float,
        timestamp: str = "",
    ) -> bool:
        """
        Send a formatted candlestick pattern alert.

        Args:
            symbol: Trading pair (e.g., "BTCUSDT").
            interval: Timeframe (e.g., "4h").
            pattern_name: Detected pattern name (e.g., "Engulfing").
            close_price: Candle close price.
            open_price: Candle open price.
            high: Candle high price.
            low: Candle low price.
            timestamp: Optional formatted timestamp string.

        Returns:
            True if sent successfully, False otherwise.
        """
        body = (
            f"*🕯️ Candle Pattern Alert*\n\n"
            f"*Symbol:* `{symbol}`\n"
            f"*Timeframe:* `{interval}`\n"
            f"*Pattern:* `{pattern_name}`\n"
            f"*Close:* `{close_price:.2f}`\n"
            f"*Open:* `{open_price:.2f}`\n"
            f"*High:* `{high:.2f}`\n"
            f"*Low:* `{low:.2f}`"
        )

        if timestamp:
            body += f"\n*Time:* `{timestamp}`"

        return self.send_message(body, parse_mode="Markdown")
