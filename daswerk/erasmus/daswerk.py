import os

import requests
import json
from dotenv import load_dotenv

load_dotenv()
KEY = str(os.getenv('KEY'))
CHAT_ID = str(os.getenv('CHAT_ID'))

def send_data_to_telegram():
    json_file = 'Daswerk.json'

    # Load JSON file
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    links = []
    dates = []
    ddate = [] # day of week
    titles = []

    for item in data:
        message = ""

        link = item['Link']
        title = item['Title']
        date = item['Date']

        content = item["content"]
        s1 = [item.replace('\n', "") for item in content]
        s2 = [item.replace('\nx', "") for item in s1]
        s3 = [item.replace('x ', "") for item in s2]
        s4 = [item.replace('\xa0', "") for item in s3]

        content = " ".join(s4)

        # Cut content at around 350 characters, ending with a dot
        if len(content) > 350:
            # Find the last dot within the first 350 characters
            last_dot = content[:350].rfind('.')
            if last_dot != -1:
                content = content[:last_dot + 1]  # Include the dot
            else:
                # If no dot found, just cut at 350 characters
                content = content[:350] + "..."

        print(content)
        message = (title +
                   "\n📅Date: " + date +
                   "\n🗯Description: \n" + content +
                   "\n🔗: " + link)
        requests.post(f'https://api.telegram.org/bot{KEY}/sendMessage?chat_id={CHAT_ID}&text=%s' % message)


    # print(dates)
    #print("Datum:", dates[0])
    #print("Titel:",titles[0])
    #print("Link:",links[0])




send_data_to_telegram()