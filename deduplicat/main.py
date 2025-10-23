import scrapy
import json
from datetime import datetime
import asyncio
from telegram import Bot
from telegram.constants import ParseMode


# 🔹 Your Telegram credentials
TELEGRAM_TOKEN = "8351086651:AAGWf57Dz9QX1kbN4knJ21unk4bDsDiQjCg"

# 🔹 Two different channels:
CHANNEL_TODAY = "-1003100621159"  # channel for today's events
CHANNEL_ALL = "-1002816889809"    # channel for all events


class GoodnightSpider(scrapy.Spider):
    name = "goodnight"
    allowed_domains = ["goodnight.at"]

    today_date = datetime.today().strftime("%Y-%m-%d")

    custom_settings = {
        "FEEDS": {
            "Goodnight.json": {"format": "json", "overwrite": True, "encoding": "utf-8"}
        }
    }

    def start_requests(self):
        # Get 4 days of data
        url = f"https://goodnight.at/api/grouped-events?date={self.today_date}&days=4"
        yield scrapy.Request(url, callback=self.parse_api)

    async def send_to_telegram(self, chat_id: str, message: str):
        """Send formatted message to Telegram"""
        bot = Bot(token=TELEGRAM_TOKEN)
        async with bot:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.HTML)

    def parse_api(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("❌ Failed to decode JSON from API")
            return

        grouped = data.get("groupedEvents") or data.get("data") or []
        if not grouped:
            self.logger.warning("⚠️ No events found")
            self.logger.debug(response.text[:500])
            return

        for day in grouped:
            date_raw = day.get("date")
            for ev in day.get("events", []):
                title = ev.get("title", "Unknown Event")
                location = (ev.get("location") or {}).get("title", "Unknown Venue")
                link = ev.get("event_link", "")
                desc = ev.get("teaser_text", "No description available.")
                start = ev.get("time_start", "Unknown Time")

                # Combine date + time
                date_full = f"{date_raw} {start}" if start else date_raw

                # Telegram message formatting (like Viennale example)
                message = (
                    f"<b>{title}</b>\n"
                    f"📅 <b>Date:</b> {date_full}\n"
                    f"📍 <b>Venue:</b> {location}\n"
                    f"📝 <b>Description:</b>\n{desc}\n"
                )
                if link:
                    message += f"🔗 <a href='{link}'>View Event</a>"

                # Decide where to send
                if date_raw == self.today_date:
                    asyncio.get_event_loop().create_task(
                        self.send_to_telegram(CHANNEL_TODAY, message)
                    )

                # Always send to all events channel
                asyncio.get_event_loop().create_task(
                    self.send_to_telegram(CHANNEL_ALL, message)
                )

                # Save JSON
                yield {
                    "Title": title,
                    "Venue": location,
                    "Date": date_full,
                    "Description": desc,
                    "Link": link,
                }
