 'EOF'
import os
import requests
import json

print("🔥 СРОЧНЫЙ ТЕСТ OPENROUTER")
print("="*50)

API_KEY = os.environ.get("OPENROUTER_API_KEY")
print(f"Ключ в системе: {'ЕСТЬ' if API_KEY else 'НЕТ'}")

if not API_KEY:
    print("❌ Ключ не найден! Выполните:")
    print('   export OPENROUTER_API_KEY="sk-or-v1-ваш_ключ"')
    exit(1)

# Тест с разными моделями
models = [
    "google/gemma-7b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "openai/gpt-3.5-turbo"
]

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "HTTP-Referer": "https://github.com",
    "Content-Type": "application/json"
}

for model in models:
    print(f"\n🔄 Тестирую модель: {model}")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Привет, как дела?"}],
        "max_tokens": 30
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            reply = data['choices'][0]['message']['content'].strip()
            print(f"   ✅ Ответ: {reply}")
            print(f"   🎯 МОДЕЛЬ РАБОТАЕТ!")
            break
        elif response.status_code == 402:
            print("   ❌ Недостаточно средств на счету")
        elif response.status_code == 401:
            print("   ❌ Неверный API ключ")
        elif response.status_code == 429:
            print("   ❌ Слишком много запросов")
        else:
            print(f"   ❌ Ошибка: {response.text[:100]}")
            
    except Exception as e:
        print(f"   ❌ Сетевая ошибка: {e}")

print("\n" + "="*50)
print("📊 РЕЗУМЕ ТЕСТА:")
if API_KEY:
    print("✅ Ключ загружен в систему")
    print("⚠️  Если все модели отказали:")
    print("   1. Проверьте баланс на https://openrouter.ai")
    print("   2. Обновите ключ в настройках")
else:
    print("❌ Ключ не найден в окружении")
EOF
