# bot_http_fast.py
import os
import asyncio
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TimedOut, NetworkError

print("=" * 70)
print("🚀 БОТ НА HTTP С УВЕЛИЧЕННЫМИ ТАЙМАУТАМИ")
print("=" * 70)

# Отключаем SSL проверки для скорости
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Читаем конфиг
with open('config.yaml', 'r', encoding='utf-8-sig') as f:
    config = yaml.safe_load(f)

TOKEN = config['telegram']['token']
BASE_URL = config['telegram'].get('base_url', 'https://api.telegram.org')

print(f"✅ Токен: {TOKEN[:15]}...")
print(f"🌐 Использую базовый URL: {BASE_URL}")

# === КОМАНДЫ ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    welcome = "👋 Привет! Бот работает на HTTP (быстрая версия)"
    await update.message.reply_text(welcome)

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда"""
    await update.message.reply_text("✅ Тест пройден! Сообщение доставлено.")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Проверка связи"""
    await update.message.reply_text("🏓 Понг! Бот активен.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    user_text = update.message.text
    await update.message.reply_text(f"📨 Получил: '{user_text}'")

# === ЗАПУСК ===

def main():
    """Запуск бота с HTTP"""
    try:
        # Создаем Application с HTTP и огромными таймаутами
        application = (
            Application.builder()
            .token(TOKEN)
            .base_url(BASE_URL)  # Используем наш HTTP URL
            .connect_timeout(120.0)   # 2 минуты!
            .read_timeout(120.0)      # 2 минуты!
            .write_timeout(120.0)     # 2 минуты!
            .pool_timeout(120.0)      # 2 минуты!
            .get_updates_connect_timeout(120.0)
            .get_updates_read_timeout(120.0)
            .get_updates_write_timeout(120.0)
            .get_updates_pool_timeout(120.0)
            .build()
        )
        
        # Обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test))
        application.add_handler(CommandHandler("ping", ping))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("⏳ Запускаю polling с 120-секундными таймаутами...")
        
        # Запускаем polling
        application.run_polling(
            poll_interval=10.0,        # Очень большой интервал
            timeout=120,               # 2 минуты!
            drop_pending_updates=True,
            bootstrap_retries=10,      # 10 попыток при запуске
            connect_timeout=120.0,
            read_timeout=120.0,
            write_timeout=120.0,
            pool_timeout=120.0,
            allowed_updates=["message"]  # Только сообщения для скорости
        )
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {type(e).__name__}")
        print(f"Сообщение: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()