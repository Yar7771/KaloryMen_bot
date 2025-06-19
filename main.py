import os
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import openai

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь фото еды — я скажу, сколько там калорий 🍒")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Фото получено! Я анализирую... 🍽")

    photo_file = await update.message.photo[-1].get_file()
    file_path = "/tmp/photo.jpg"
    await photo_file.download_to_drive(file_path)

    with open(file_path, "rb") as image_file:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ты нутрициолог. Определи калорийность по фото еды."},
                {"role": "user", "content": "Что на этом фото и сколько это калорий?", "image": image_file}
            ],
            max_tokens=300
        )

    result = response.choices[0].message.content
    await update.message.reply_text(result)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()