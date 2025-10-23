import scrapy
import json
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
import asyncio

# === TELEGRAM CONFIG ===
TELEGRAM_TOKEN = "8351086651:AAGWf57Dz9QX1kbN4knJ21unk4bDsDiQjCg"
TELEGRAM_CHAT_ID = "-1003100621159"

class GoodnightSpider(scrapy.Spider):
    name = "goodnight"
    allowed_domains = ["goodnight.at"]

    # Automatically use today's date
    date = datetime.now().strftime("%Y-%m-%d")

    custom_settings = {
        "FEEDS": {"Goodnight.json": {"format": "json", "overwrite": True, "encoding": "utf-8"}},
    }

    sent_events = set()  # for duplicate prevention

    def start_requests(self):
        url = f"https://goodnight.at/api/grouped-events?date={self.date}&days=1"
        yield scrapy.Request(url, callback=self.parse_api)

    def parse_api(self, response):
        try:
            data = json.loads(response.text)
        except json.JSONDecodeError:
            self.logger.error("Failed to decode JSON from API")
            return

        grouped = data.get("groupedEvents") or data.get("data") or []
        if not grouped:
            self.logger.warning("No grouped data found")
            return

        for day in grouped:
            if day.get("date") != self.date:
                continue

            for ev in day.get("events", []):
                title = ev.get("title", "Untitled Event").strip()
                location = (ev.get("location") or {}).get("title", "Unknown Location")
                link = ev.get("event_link")
                desc = ev.get("teaser_text", "No description available.")
                start = ev.get("time_start", "")
                date_full = f"{day.get('date')} {start}" if start else day.get("date")

                # Skip duplicates
                unique_key = f"{title}-{date_full}"
                if unique_key in self.sent_events:
                    continue
                self.sent_events.add(unique_key)

                event = {
                    "Title": title,
                    "Venue": location,
                    "Date": date_full,
                    "Description": desc,
                    "Link": link or "No link available.",
                }

                yield event

                # If event has a link, try to fetch image
                if link:
                    yield scrapy.Request(link, callback=self.parse_image, meta={"event": event})
                else:
                    asyncio.run(self.send_to_telegram(event, image_url=None))

    def parse_image(self, response):
        """Try to extract event image from HTML if available."""
        event = response.meta["event"]
        image_url = response.css("img::attr(src)").get()
        if image_url and image_url.startswith("/"):
            image_url = f"https://goodnight.at{image_url}"
        asyncio.run(self.send_to_telegram(event, image_url=image_url))

    async def send_to_telegram(self, event, image_url=None):
        """Send nicely formatted message to Telegram."""
        bot = Bot(token=TELEGRAM_TOKEN)

        text = (
            f"<b>{event['Title']}</b>\n"
            f"📅 <b>Date:</b> {event['Date']}\n"
            f"🏛 <b>Venue:</b> {event['Venue']}\n"
            f"🗒 <b>Description:</b> {event['Description']}\n"
            f"🔗 <b>More info:</b> {event['Link']}"
        )

        async with bot:
            if image_url:
                await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=image_url, caption=text, parse_mode=ParseMode.HTML)
            else:
                await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text, parse_mode=ParseMode.HTML)
