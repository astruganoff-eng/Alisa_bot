import os
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Фиксы для Windows
os.environ['TELEGRAM_BOT_HTTP_CLIENT'] = 'sync'

# Импортируем менеджер персонажей
from personas.persona_manager import PersonaManager

print("=" * 60)
print("🤖 ТЕЛЕГРАМ БОТ С ПЕРЕКЛЮЧЕНИЕМ ПЕРСОНАЖЕЙ")
print("=" * 60)

# Читаем конфиг
with open('config.yaml', 'r', encoding='utf-8-sig') as f:
    config = yaml.safe_load(f)

TOKEN = config['telegram']['token']

# Создаем менеджер персонажей
persona_manager = PersonaManager()

# === КОМАНДЫ БОТА ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - приветствие"""
    welcome_text = """
👋 Привет! Я бот с двумя персонажами:

👤 *МАРК* (28 лет) - программист, спортсмен, с чувством юмора
💫 *АЛИСА* (25 лет) - дизайнер, творческая, тёплая

*КОМАНДЫ:*
/mark - переключиться на Марка
/alisa - переключиться на Алису
/who - кто сейчас говорит
/personas - список персонажей
/clear - очистить историю диалога

Просто выбери персонажа и начни общение!"""
    
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def switch_to_mark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключиться на Марка"""
    user_id = update.effective_user.id
    persona_manager.set_active_persona(user_id, "mark")
    
    persona_info = persona_manager.get_persona_info(user_id)
    await update.message.reply_text(
        f"👤 Теперь ты общаешься с *{persona_info['name']}*!\n"
        f"Возраст: {persona_info['age']}, {persona_info['gender'] == 'male' and 'мужчина' or 'девушка'}\n\n"
        "Привет! Рад тебя видеть! 👋",
        parse_mode='Markdown'
    )

async def switch_to_alisa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Переключиться на Алису"""
    user_id = update.effective_user.id
    persona_manager.set_active_persona(user_id, "alisa")
    
    persona_info = persona_manager.get_persona_info(user_id)
    await update.message.reply_text(
        f"💫 Теперь ты общаешься с *{persona_info['name']}*!\n"
        f"Возраст: {persona_info['age']}, {persona_info['gender'] == 'female' and 'девушка' or 'парень'}\n\n"
        "Привет! Рада тебя видеть! 💕",
        parse_mode='Markdown'
    )

async def who_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Кто сейчас активен"""
    user_id = update.effective_user.id
    persona_info = persona_manager.get_persona_info(user_id)
    
    if "error" in persona_info:
        await update.message.reply_text(
            "Персонаж ещё не выбран!\n"
            "Используй /mark или /alisa"
        )
    else:
        emoji = "👤" if persona_info['gender'] == 'male' else "💫"
        await update.message.reply_text(
            f"{emoji} Сейчас с тобой говорит *{persona_info['name']}*\n"
            f"Возраст: {persona_info['age']}",
            parse_mode='Markdown'
        )

async def list_personas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Список доступных персонажей"""
    personas = persona_manager.get_available_personas()
    
    text = "📋 *Доступные персонажи:*\n\n"
    for p in personas:
        gender_emoji = "👨" if p['gender'] == 'male' else "👩"
        text += f"{gender_emoji} *{p['name']}* ({p['age']} лет)\n"
        text += f"   Ключ: `{p['key']}`\n"
        text += f"   Выбрать: /{p['key']}\n\n"
    
    await update.message.reply_text(text, parse_mode='Markdown')

async def clear_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить историю диалога"""
    user_id = update.effective_user.id
    if user_id in persona_manager.conversation_history:
        # Оставляем только системный промпт
        persona_key = persona_manager.active_personas.get(user_id)
        if persona_key:
            persona = persona_manager.personas[persona_key]
            persona_manager.conversation_history[user_id] = [{
                "role": "system",
                "content": persona.system_prompt
            }]
        
        await update.message.reply_text("🗑️ История диалога очищена!")
    else:
        await update.message.reply_text("У тебя ещё нет истории диалога")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    user_id = update.effective_user.id
    message_text = update.message.text
    
    # Проверяем, выбран ли персонаж
    persona_info = persona_manager.get_persona_info(user_id)
    if not persona_info or "error" in persona_info:
        await update.message.reply_text(
            "Сначала выбери персонажа!\n"
            "/mark - общаться с Марком\n"
            "/alisa - общаться с Алисой"
        )
        return
    
    # Показываем, что бот "печатает"
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Генерируем ответ через LM Studio
    reply = persona_manager.generate_response(
        user_id=user_id,
        message=message_text,
        use_lmstudio=True  # Меняй на False для теста без LM Studio
    )
    
    # Отправляем ответ
    await update.message.reply_text(reply)

# === ЗАПУСК БОТА ===

def main():
    """Основная функция запуска"""
    print("✅ Персонажи загружены")
    print(f"✅ Токен: {TOKEN[:15]}...")
    
    # Создаем Application
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mark", switch_to_mark))
    application.add_handler(CommandHandler("alisa", switch_to_alisa))
    application.add_handler(CommandHandler("who", who_command))
    application.add_handler(CommandHandler("personas", list_personas))
    application.add_handler(CommandHandler("clear", clear_history))
    
    # Обработчик текстовых сообщений
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    ))
    
    print("🚀 Запускаю бота...")
    application.run_polling(
        poll_interval=2.0,
        timeout=60,
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()