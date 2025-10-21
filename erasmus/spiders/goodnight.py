import scrapy
import json
from datetime import datetime


class GoodnightSpider(scrapy.Spider):
    name = "goodnight"
    allowed_domains = ["goodnight.at"]
    # You can parameterize the date later
    date = "2025-10-21"

    custom_settings = {
        "FEEDS": {
            "Goodnight.json": {"format": "json", "overwrite": True, "encoding": "utf-8"}
        }
    }

    def start_requests(self):
        url = f"https://goodnight.at/api/grouped-events?date={self.date}&days=4"
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
            self.logger.debug(response.text[:500])
            return

        for day in grouped:
            date_raw = day.get("date")
            for ev in day.get("events", []):
                title = ev.get("title")
                location = (ev.get("location") or {}).get("title")
                link = ev.get("event_link")
                desc = ev.get("teaser_text", "")
                start = ev.get("time_start")

                # combine date + time
                date_full = f"{date_raw} {start}" if start else date_raw

                yield {
                    "Title": title,
                    "Venue": location,
                    "Date": date_full,
                    "Description": desc,
                    "Link": link,
                }






