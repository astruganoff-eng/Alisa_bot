# bot_no_ssl.py
import os
import ssl
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

print("=" * 60)
print("🤖 БОТ БЕЗ SSL ПРОВЕРОК")
print("=" * 60)

# 1. Отключаем SSL проверки
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# 2. Используем sync клиент
os.environ['TELEGRAM_BOT_HTTP_CLIENT'] = 'sync'

# 3. Читаем токен
with open('config.yaml', 'r', encoding='utf-8-sig') as f:
    TOKEN = yaml.safe_load(f)['telegram']['token']

print(f"✅ Токен: {TOKEN[:15]}...")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔓 Бот без SSL работает!")

try:
    print("🚀 Создаю Application с отключенным SSL...")
    
    # Создаем Application с кастомным SSL контекстом
    application = (
        Application.builder()
        .token(TOKEN)
        .connect_timeout(120.0)  # 2 минуты
        .read_timeout(120.0)     # 2 минуты
        .get_updates_connect_timeout(120.0)
        .get_updates_read_timeout(120.0)
        .build()
    )
    
    application.add_handler(CommandHandler("start", start))
    
    print("⏳ Запускаю polling (таймаут 120 сек)...")
    application.run_polling(
        poll_interval=5.0,
        timeout=120,
        drop_pending_updates=True,
        bootstrap_retries=5
    )
    
except Exception as e:
    print(f"❌ Ошибка: {type(e).__name__}: {e}")