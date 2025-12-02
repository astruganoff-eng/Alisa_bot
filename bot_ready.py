import os
import requests
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print("="*60)
print("🤖 ТЕЛЕГРАМ БОТ С ИИ — ГОТОВ К РАБОТЕ")
print("="*60)

# Ключ (уже установлен в окружении)
API_KEY = os.environ.get("OPENROUTER_API_KEY")
if not API_KEY:
    print("❌ ОШИБКА: OPENROUTER_API_KEY не найден!")
    print("Выполните: export OPENROUTER_API_KEY='ваш_ключ'")
    exit(1)

TOKEN = "7691758181:AAGYaxUjVYwS6C7Vh6xqiqEkBgLuMglBq9w"

# Персонажи
class Persona:
    def __init__(self, name, description, traits):
        self.name = name
        self.description = description
        self.traits = traits
        self.system_prompt = f"""Ты {name}, {description}.
Особенности: {traits}
Отвечай естественно, как живой человек, 1-2 предложениями."""
        self.fallback_responses = [
            f"Привет! Я {name}. Рад тебя видеть!",
            f"Ой, что-то я задумался... Так ты о чём?",
            f"Интересно! А расскажи подробнее?",
            f"Ммм, хороший вопрос. Дай подумать...",
            f"Я {name}, если что забыл! 😊"
        ]

# Создаём персонажей
MARK = Persona(
    name="Марк",
    description="28 лет, программист, спортсмен",
    traits="технарь, логичный, с чувством юмора, любит спорт и технологии"
)

ALISA = Persona(
    name="Алиса", 
    description="25 лет, дизайнер, творческая личность",
    traits="креативная, эмоциональная, любит искусство, модная, общительная"
)

PERSONAS = {"mark": MARK, "alisa": ALISA}
active_users = {}

# Функция запроса к ИИ
def ask_ai(persona, user_message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "HTTP-Referer": "https://github.com/astruganoff-eng/Mark_Alisa_bot",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mistralai/mistral-7b-instruct:free",
        "messages": [
            {"role": "system", "content": persona.system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 150,
        "temperature": 0.8
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].strip()
        else:
            print(f"❌ Ошибка API: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка сети: {e}")
    
    return None

# Команды бота
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 *Привет! Это бот с настоящим ИИ* 🧠\n\n"
        "Выбери персонажа:\n"
        "👤 /mark — Марк (программист, 28 лет)\n"
        "💫 /alisa — Алиса (дизайнер, 25 лет)\n\n"
        "После выбора просто пиши сообщения!",
        parse_mode='Markdown'
    )

async def mark_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_users[user_id] = "mark"
    await update.message.reply_text(
        "👤 *Активирован режим: Марк!*\n\n"
        "Привет! Я Марк, программист и спортсмен. "
        "Люблю технологии, код и пробежки по утрам. "
        "Что у тебя нового? 💻🏃‍♂️",
        parse_mode='Markdown'
    )

async def alisa_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    active_users[user_id] = "alisa"
    await update.message.reply_text(
        "💫 *Активирован режим: Алиса!*\n\n"
        "Привет, милый! Я Алиса, дизайнер и творческая душа. "
        "Обожаю искусство, моду и красивые вещи. "
        "Расскажи что-нибудь интересное! 🎨💕",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if user_id not in active_users:
        await update.message.reply_text("Сначала выбери персонажа: /mark или /alisa")
        return
    
    persona_name = active_users[user_id]
    persona = PERSONAS[persona_name]
    
    # Показываем "печатает"
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )
    
    # Получаем ответ от ИИ
    ai_reply = ask_ai(persona, update.message.text)
    
    if ai_reply:
        await update.message.reply_text(ai_reply)
        print(f"✅ [AI] {persona.name}: {ai_reply[:60]}...")
    else:
        # Запасной ответ
        fallback = random.choice(persona.fallback_responses)
        await update.message.reply_text(fallback)
        print(f"⚠️ [FALLBACK] {persona.name}")

# Запуск
def main():
    print(f"✅ OpenRouter ключ: {API_KEY[:20]}...")
    print(f"✅ Telegram токен: {TOKEN[:15]}...")
    print("✅ Персонажи готовы")
    print("🚀 Запускаю бота...")
    
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("mark", mark_cmd))
    app.add_handler(CommandHandler("alisa", alisa_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("="*60)
    print("🤖 Бот запущен! Пишите в Telegram: @ваш_бот")
    print("="*60)
    
    app.run_polling()

if __name__ == "__main__":
    main()
