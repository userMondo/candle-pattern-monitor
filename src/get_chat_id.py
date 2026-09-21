"""
Helper script to find your Telegram chat ID.

Run this after you've sent a message to your bot (from your Telegram account).

Usage:
    python3 src/get_chat_id.py --token YOUR_BOT_TOKEN
"""
import argparse
import requests
import sys
import os

def get_chat_id(token: str) -> None:
    """Fetch chat ID from Telegram getUpdates."""
    url = f"https://api.telegram.org/bot{token}/getUpdates"

    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()

        if not data.get("ok"):
            print(f"❌ Error: {data.get('description', 'Unknown error')}")
            print("   - The bot token may be invalid or revoked.")
            print("   - Create a new bot via @BotFather and try again.")
            return

        updates = data.get("result", [])
        if not updates:
            print("⚠️  No updates found.")
            print("   - You need to send a message to your bot first.")
            print("   - Open Telegram, find your bot, and send any message (e.g., '/start').")
            print("   - Then run this script again.")
            return

        print("Found chat(s):")
        for update in updates:
            chat = update.get("message", {}).get("chat", {})
            if chat:
                chat_id = chat.get("id")
                first_name = chat.get("first_name", "N/A")
                username = chat.get("username", "N/A")
                chat_type = chat.get("type", "N/A")
                print(f"  Chat ID: {chat_id}")
                print(f"  Name: {first_name}")
                print(f"  Username: @{username}")
                print(f"  Type: {chat_type}")

    except requests.RequestException as e:
        print(f"❌ Network error: {e}")


def test_bot(token: str) -> bool:
    """Test if the bot token is valid."""
    url = f"https://api.telegram.org/bot{token}/getMe"
    try:
        resp = requests.get(url, timeout=30)
        data = resp.json()
        if data.get("ok"):
            bot = data.get("result", {})
            print(f"✅ Bot is valid!")
            print(f"  Name: {bot.get('first_name', 'N/A')}")
            print(f"  Username: @{bot.get('username', 'N/A')}")
            print(f"  ID: {bot.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ Bot token is invalid: {data.get('description', 'Unknown')}")
            return False
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find your Telegram chat ID")
    parser.add_argument("--token", default=os.getenv("TELEGRAM_BOT_TOKEN"),
                        help="Telegram bot token (or set TELEGRAM_BOT_TOKEN env var)")
    args = parser.parse_args()

    if not args.token:
        print("Usage: python3 src/get_chat_id.py --token YOUR_BOT_TOKEN")
        print("Or set TELEGRAM_BOT_TOKEN environment variable.")
        sys.exit(1)

    test_bot(args.token)
    print()
    get_chat_id(args.token)
