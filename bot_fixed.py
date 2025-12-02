# bot_fixed.py
import os
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("=" * 60)
print("🤖 БОТ С ИСПРАВЛЕННОЙ ОШИБКОЙ URL")
print("=" * 60)

# Старый добрый sync клиент
os.environ['TELEGRAM_BOT_HTTP_CLIENT'] = 'sync'

# Читаем конфиг
with open('config.yaml', 'r', encoding='utf-8-sig') as f:
    config = yaml.safe_load(f)

TOKEN = config['telegram']['token']
print(f"✅ Токен: {TOKEN[:15]}...")

# === КОМАНДЫ ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    await update.message.reply_text("👋 Бот работает! Исправлена ошибка URL")

async def test(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Тестовая команда"""
    await update.message.reply_text("✅ Тест пройден!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений"""
    text = update.message.text
    await update.message.reply_text(f"📨 Получил: {text}")

# === ЗАПУСК ===

def main():
    """Основной запуск"""
    try:
        # Создаем Application БЕЗ base_url (используем по умолчанию)
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("test", test))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("🚀 Запускаю бота...")
        
        # Запускаем polling с нормальными таймаутами
        application.run_polling(
            poll_interval=3.0,
            timeout=30,
            drop_pending_updates=True
        )
        
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}")
        print(f"Сообщение: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()