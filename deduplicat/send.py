import scrapy
import json
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.constants import ParseMode
import os
import hashlib


TELEGRAM_TOKEN = "8351086651:AAGWf57Dz9QX1kbN4knJ21unk4bDsDiQjCg"
FRIENDS_CHANNEL = "-4970559898"


class GoodnightSpider(scrapy.Spider):
    name = "goodnight"
    allowed_domains = ["goodnight.at"]

    today_date = datetime.today().strftime("%Y-%m-%d")

    custom_settings = {
        "FEEDS": {
            "Goodnight.json": {"format": "json", "overwrite": True, "encoding": "utf-8"}
        }
    }

    sent_hashes_file = "sent_events.txt"

    def start_requests(self):
        # Create file if missing
        if not os.path.exists(self.sent_hashes_file):
            open(self.sent_hashes_file, "w").close()

        url = f"https://goodnight.at/api/grouped-events?date={self.today_date}&days=4"
        yield scrapy.Request(url, callback=self.parse_api)

    async def send_to_telegram(self, message: str):
        """Send formatted message to Telegram channel"""
        bot = Bot(token=TELEGRAM_TOKEN)
        async with bot:
            await bot.send_message(
                chat_id=FRIENDS_CHANNEL, text=message, parse_mode=ParseMode.HTML
            )

    def is_duplicate(self, title, date, venue):
        """Check if event already sent"""
        event_id = hashlib.md5(f"{title}-{date}-{venue}".encode()).hexdigest()

        with open(self.sent_hashes_file, "r") as f:
            sent_ids = f.read().splitlines()

        if event_id in sent_ids:
            return True

        with open(self.sent_hashes_file, "a") as f:
            f.write(event_id + "\n")

        return False

    def parse_api(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("❌ Failed to decode JSON from API")
            return

        grouped = data.get("groupedEvents") or data.get("data") or []
        if not grouped:
            self.logger.warning("⚠️ No events found")
            return

        for day in grouped:
            date_raw = day.get("date")
            for ev in day.get("events", []):
                title = ev.get("title", "Unknown Event")
                location = (ev.get("location") or {}).get("title", "Unknown Venue")
                link = ev.get("event_link", "")
                desc = ev.get("teaser_text", "No description available.")
                start = ev.get("time_start", "Unknown Time")


                date_full = f"{date_raw} {start}" if start else date_raw


                if self.is_duplicate(title, date_full, location):
                    continue


                message = (
                    f"<b>{title}</b>\n"
                    f"📅 <b>Date:</b> {date_full}\n"
                    f"📍 <b>Venue:</b> {location}\n"
                    f"📝 <b>Description:</b>\n{desc}\n"
                )
                if link:
                    message += f"🔗 <a href='{link}'>View Event</a>"

                asyncio.get_event_loop().create_task(self.send_to_telegram(message))

                yield {
                    "Title": title,
                    "Venue": location,
                    "Date": date_full,
                    "Description": desc,
                    "Link": link,
                }
