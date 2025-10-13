from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from daswerk_spider import get_daswerk_events
from telegram_sender import send_event_to_telegram
import asyncio
import nest_asyncio  # 👈 toto pridáme

nest_asyncio.apply()  # 👈 opraví problém s event loopom

TOKEN = "8351086651:AAGWf57Dz9QX1kbN4knJ21unk4bDsDiQjCg"

async def event_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Načítavam eventy z Das Werk...")
    events = get_daswerk_events()
    send_event_to_telegram(events)

async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("event", event_command))
    print("✅ Bot beží! Napíš /event v Telegrame")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
