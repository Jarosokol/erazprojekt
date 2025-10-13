import requests
from parsel import Selector


def get_daswerk_events():
    url = "https://www.daswerk.org/programm"
    response = requests.get(url)

    if response.status_code != 200:
        print("❌ Nepodarilo sa načítať stránku Das Werk")
        return []

    selector = Selector(response.text)
    events = []

    for event in selector.css('div.fusion-post-content-wrapper'):
        name = event.css('h2::text').get()
        date = event.css('.fusion-post-content p::text').get()
        link = event.css('a::attr(href)').get()

        if name and date:
            events.append({
                "name": name.strip(),
                "date": date.strip(),
                "link": link
            })

    return events
