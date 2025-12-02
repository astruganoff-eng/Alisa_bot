cat > bot_fixed_now.py << 'EOF'
import os
import yaml
import requests
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("=" * 60)
print("🤖 БОТ С OPENROUTER AI (РАБОЧАЯ ВЕРСИЯ)")
print("=" * 60)

# === ПРОВЕРКА КЛЮЧА ===
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    print("❌ ОШИБКА: OPENROUTER_API_KEY не установлен!")
    print("")
    print("📋 КАК ИСПРАВИТЬ:")
    print("1. Зайди на https://openrouter.ai")
    print("2. Войди в аккаунт (Sign in)")
    print("3. Нажми 'Settings' → 'API Keys'")
    print("4. Создай новый ключ (Create new key)")
    print("5. Скопируй его")
    print("6. На PythonAnywhere выполни:")
    print("   export OPENROUTER_API_KEY='твой_ключ_здесь'")
    print("7. Перезапусти бота")
    print("=" * 60)
    exit(1)

print(f"✅ OpenRouter ключ: {OPENROUTER_API_KEY[:15]}...")

# === ТЕЛЕГРАМ ТОКЕН ===
TOKEN = "7691758181:AAGYaxUjVYwS6C7Vh6xqiqEkBgLuMglBq9w"
print(f"✅ Telegram токен: {TOKEN[:15]}...")

# === ИМПОРТ ПЕРСОНАЖЕЙ ===
from personas.mark_male import MarkPersona
from personas.alisa_female import AlisaPersona

PERSONAS = {
    "mark": MarkPersona(),
    "alisa": AlisaPersona()
}
active_users = {}  # user_id -> persona_name

# === OPENROUTER ЗАПРОС ===
def ask_openrouter(persona, user_message, user_id):
    """Спрашиваем OpenRouter"""
    
    print(f"\n🧠 Запрос от пользователя {user_id}:")
    print(f"   Персонаж: {persona.name}")
    print(f"   Сообщение: {user_message}")
    
    # Подготовка запроса
    messages = [
        {"role": "system", "content": persona.system_prompt},
        {"role": "user", "content": user_message}
    ]
    
    payload = {
        "model": "google/gemma-7b-it:free",
        "messages": messages,
        "max_tokens": 150,
        "temperature": 0.8
    }
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/astruganoff-eng/Mark_Alisa_bot",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20
        )
        
        print(f"📡 Статус OpenRouter: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            reply = result['choices'][0]['message']['content']
            print(f"✅ Ответ AI: {reply[:80]}...")
            return reply
        else:
            print(f"❌ Ошибка {response.status_code}: {response.text[:100]}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
        return None

# === КОМАНДЫ ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Привет! Я бот с ИИ от OpenRouter* 🧠\n\n"
        "Выбери персонажа:\n"
        "👤 /mark - Марк (28 лет, программист)\n"
        "💫 /alisa - Алиса (25 лет, дизайнер)",
        parse_mode='Markdown'
    )

async def mark_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_users[user_id] = "mark"
    await update.message.reply_text(
        "👤 *Теперь ты общаешься с Марком!*\n"
        "28 лет, программист, спортсмен\n\n"
        "Привет! Я тут. Что расскажешь? 👋",
        parse_mode='Markdown'
    )

async def alisa_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_users[user_id] = "alisa"
    await update.message.reply_text(
        "💫 *Теперь ты общаешься с Алисой!*\n"
        "25 лет, дизайнер, творческая\n\n"
        "Привет, милый! Рада тебя видеть! 💕",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in active_users:
        await update.message.reply_text("Сначала выбери персонажа: /mark или /alisa")
        return
    
    persona_name = active_users[user_id]
    persona = PERSONAS[persona_name]
    user_message = update.message.text
    
    # Печатает...
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Пробуем OpenRouter
    ai_reply = ask_openrouter(persona, user_message, user_id)
    
    if ai_reply:
        # Успешный ответ от AI
        await update.message.reply_text(ai_reply)
    else:
        # OpenRouter не сработал - случайная фраза
        fallback = random.choice(persona.fallback_responses)
        await update.message.reply_text(fallback)

# === ЗАПУСК ===
def main():
    print("🚀 Запускаю бота...")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mark", mark_cmd))
    app.add_handler(CommandHandler("alisa", alisa_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
EOF

# Запусти исправленного бота
python bot_fixed_now.py
