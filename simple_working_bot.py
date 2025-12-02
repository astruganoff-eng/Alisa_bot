# simple_working_bot.py
import os
os.environ['TELEGRAM_BOT_HTTP_CLIENT'] = 'sync'

import yaml
with open('config.yaml', 'r', encoding='utf-8-sig') as f:
    TOKEN = yaml.safe_load(f)['telegram']['token']

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎉 ПРОСТОЙ БОТ РАБОТАЕТ!")

print("🔥 Запускаю простейшего бота...")
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.run_polling()