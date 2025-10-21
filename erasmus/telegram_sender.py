import sys
import types
import json
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
from datetime import datetime

# 🩹 Fix for Python 3.13 (imghdr removed)
if 'imghdr' not in sys.modules:
    imghdr = types.ModuleType("imghdr")
    def what(file, h=None): return None
    imghdr.what = what
    sys.modules['imghdr'] = imghdr

# --- CONFIG ---
TELEGRAM_TOKEN = "8351086651:AAGWf57Dz9QX1kbN4knJ21unk4bDsDiQjCg"   # 🟡 Replace with your bot token
CHAT_ID = "-1002816889809"            # 🟡 Replace with your chat ID
JSON_FILE = "goodnight.json"             # Path to JSON file with scraped data


async def send_to_telegram(message: str):
    """Send one message to Telegram."""
    bot = Bot(token=TELEGRAM_TOKEN)
    async with bot:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message,
            parse_mode=ParseMode.HTML
        )


def format_event(event):
    """Format event info nicely for Telegram."""
    title = f"<b>{event.get('Title', 'No title')}</b>"
    date = event.get('Date', 'N/A')
    venue = event.get('Venue', 'N/A')
    desc = event.get('Description', '')
    link = event.get('Link', '')

    msg = f"📅 <b>{date}</b>\n📍 <i>{venue}</i>\n\n{desc}"
    if link:
        msg += f"\n\n🔗 <a href='{link}'>More info</a>"

    return f"{title}\n\n{msg}"


async def main():
    """Read JSON and send all events."""
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"⚠️ Could not read {JSON_FILE}: {e}")
        return

    if not data:
        print("⚠️ No events found in JSON.")
        return

    print(f"📨 Sending {len(data)} events to Telegram...")
    for item in data[:10]:  # send first 10 to avoid spam
        msg = format_event(item)
        await send_to_telegram(msg)
        await asyncio.sleep(1.5)  # avoid Telegram rate limit

    print("✅ Done sending events!")


if __name__ == "__main__":
    asyncio.run(main())
