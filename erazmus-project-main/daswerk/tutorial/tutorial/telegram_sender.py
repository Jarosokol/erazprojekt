
import requests

TOKEN = "8351086651:AAGWf57Dz9QX1kbN4knJ21unk4bDsDiQjCg"
CHAT_ID = "-1002816889809"

def send_event_to_telegram(events):
    if not events:
        text = "⚠️ Žiadne eventy sa nenašli na stránke Das Werk."
    else:
        text = "🎶 *Das Werk – nadchádzajúce eventy:*\n\n"
        for e in events[:5]:
            text += f"🎉 *{e['name']}*\n📅 {e['date']}\n🔗 [Viac info]({e['link']})\n\n"

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown", "disable_web_page_preview": True}
    requests.post(url, data=payload)
