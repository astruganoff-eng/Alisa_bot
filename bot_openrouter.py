# bot_openrouter.py
import os
import yaml
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройки OpenRouter
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', 'твой_ключ_здесь')

print("=" * 60)
print("🤖 БОТ С OPENROUTER AI")
print("=" * 60)

# Читаем конфиг
with open('config.yaml', 'r', encoding='utf-8') as f:
    TOKEN = yaml.safe_load(f)['telegram']['token']

print(f"Токен: {TOKEN[:15]}...")

# Импортируем персонажей
from personas.mark_male import MarkPersona
from personas.alisa_female import AlisaPersona

personas = {
    "mark": MarkPersona(),
    "alisa": AlisaPersona()
}
active_personas = {}

# === ФУНКЦИИ ===

import requests

def generate_ai_response(persona, user_message, history):
    """Генерация ответа через OpenRouter"""
    
    messages = history + [{"role": "user", "content": user_message}]
    
    payload = {
        "model": "google/gemma-7b-it:free",
        "messages": [
            {"role": "system", "content": persona.system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 150,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "HTTP-Referer": "https://github.com/astruganoff-eng/Mark_Alisa_bot",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
    except:
        pass
    
    # Запасной ответ
    import random
    return random.choice(persona.fallback_responses)

# === КОМАНДЫ БОТА ===

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я умный бот с ИИ.\n"
        "Выбери персонажа:\n"
        "/mark - Марк (28 лет, программист)\n"
        "/alisa - Алиса (25 лет, дизайнер)"
    )

async def mark_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_personas[user_id] = "mark"
    await update.message.reply_text(
        "👤 Теперь ты общаешься с *Марком*!\n"
        "28 лет, программист, спортсмен\n\n"
        "Привет! Что нового? 👋",
        parse_mode='Markdown'
    )

async def alisa_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_personas[user_id] = "alisa"
    await update.message.reply_text(
        "💫 Теперь ты общаешься с *Алисой*!\n"
        "25 лет, дизайнер, творческая\n\n"
        "Привет! Рада тебя видеть! 💕",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in active_personas:
        await update.message.reply_text("Сначала выбери персонажа: /mark или /alisa")
        return
    
    persona_name = active_personas[user_id]
    persona = personas[persona_name]
    user_message = update.message.text
    
    # Показываем "печатает..."
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Генерируем ответ
    reply = generate_ai_response(persona, user_message, [])
    
    await update.message.reply_text(reply)

# === ЗАПУСК ===

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("mark", mark_cmd))
    application.add_handler(CommandHandler("alisa", alisa_cmd))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("🚀 Запускаю бота с OpenRouter...")
    application.run_polling()

if __name__ == "__main__":
    main()
