import os
import openai
import base64
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Отправь фото еды — я скажу, сколько там калорий 🍒")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Фото получено! Я анализирую... 🍽️")

    photo = update.message.photo[-1]
    file = await photo.get_file()
    file_path = "/tmp/photo.jpg"
    await file.download_to_drive(file_path)

    with open(file_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "Ты нутрициолог. Определи калорийность по фото еды, если не уверен — скажи прямо."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Что на фото? Сколько примерно калорий в этой еде?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ]
    )

    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()
