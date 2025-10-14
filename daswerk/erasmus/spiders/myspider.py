import re
import scrapy
from datetime import datetime

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = [
        'https://www.daswerk.org/programm',
    ]

    custom_settings = {
        'FEEDS': {
            'Daswerk.json': {
                'format': 'json',
                'overwrite': True,  # If the file already exists, it will overwrite it
            },
        },
    }

    def parse(self, response):
        # Route by domain to discover event links
        url = response.url
        self.logger.info(f"Scraping main page: {url}")

        links = response.css('a.preview-item--link::attr(href)').getall()

        for link in links:
            yield response.follow(link, callback=self.parse_event)

    def parse_event(self, response):
        url = response.url

        # Collect content text from main areas
        content = response.css('.detail-content ::text').getall()
        title = response.css('p.main--header-title::text').get()

        date = self.clean_date(response.css('li:nth-child(1)::text').get())
        time = response.css('li:nth-child(2)::text').get()

        today_date = datetime.strftime("%#d. %#m. %Y")
        if date != today_date:
            yield None

        yield {
            'Link': url,
            'Title': title.strip(),
            'Date': date.strip(),
            'Time': time.strip(),
            'content': content,
        }

    def clean_date(self, date):
        # Mapping German month names to numbers
        months = {
            "Januar": 1,
            "Februar": 2,
            "März": 3,
            "April": 4,
            "Mai": 5,
            "Juni": 6,
            "Juli": 7,
            "August": 8,
            "September": 9,
            "Oktober": 10,
            "November": 11,
            "Dezember": 12
        }

        # Regex to extract day, month, optional year
        match = re.search(r"\b(\d{1,2})\.?\s+(\w+)(?:\s+(\d{4}))?", date)

        if match:
            day = int(match.group(1))
            month_name = match.group(2)
            month_num = months[month_name]
            year = int(match.group(3)) if match.group(3) else datetime.now().year
            result = f"{day}. {month_num}. {year}"
            return result  # Example Output: 9. 11. [YEAR] or 9. 11. 2025 if no year in input
        return None
