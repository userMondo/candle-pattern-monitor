"""Helper: get your Telegram chat ID after messaging your bot.

Usage:
    python3 src/get_chat_id.py --token 123456789:AAFe.... --timeout 10

Steps:
1. Create a bot via @BotFather -> get token
2. Open Telegram, search for your bot, send /start
3. Run this script with the token
"""
import requests
import argparse
import sys

def get_chat_id(token: str, timeout: int = 30) -> str:
    """Fetch chat ID from Telegram getUpdates API."""
    api = f"https://api.telegram.org/bot{token}"
    resp = requests.get(f"{api}/getMe", timeout=10)
    if resp.status_code != 200:
        print(f"Bot token invalid: {resp.status_code}")
        return ""
    me = resp.json()["result"]
    print(f"Bot: {me['first_name']} (@{me['username']})")
    
    resp = requests.get(f"{api}/getUpdates?timeout={timeout}", timeout=timeout+5)
    if resp.status_code != 200:
        print(f"Failed to get updates: {resp.status_code}")
        return ""
    
    updates = resp.json().get("result", [])
    if not updates:
        print("No messages received. Send /start to your bot first, then re-run.")
        return ""
    
    chat_ids = set()
    for update in updates:
        chat = update.get("message", {}).get("chat", {})
        if chat:
            chat_ids.add(chat["id"])
    
    if chat_ids:
        chat_id = list(chat_ids)[0]
        print(f"Chat ID found: {chat_id}")
        return str(chat_id)
    else:
        print("Chat ID not found in updates.")
        return ""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get Telegram chat ID")
    parser.add_argument("--token", required=True, help="Bot token from @BotFather")
    parser.add_argument("--timeout", type=int, default=10, help="GetUpdates timeout in seconds")
    args = parser.parse_args()
    
    chat_id = get_chat_id(args.token, args.timeout)
    if chat_id:
        print(f"\nUse this in your config:")
        print(f"TELEGRAM_BOT_TOKEN={args.token}")
        print(f"TELEGRAM_CHAT_ID={chat_id}")
    else:
        sys.exit(1)
