# bot_manual_connection.py
import requests
import yaml
import time

print("=" * 60)
print("🤖 РУЧНОЕ ПОДКЛЮЧЕНИЕ К TELEGRAM API")
print("=" * 60)

# Читаем токен
with open('config.yaml', 'r', encoding='utf-8-sig') as f:
    TOKEN = yaml.safe_load(f)['telegram']['token']

print(f"Токен: {TOKEN[:15]}...")

# Пробуем разные методы подключения
urls = [
    f"https://api.telegram.org/bot{TOKEN}/getMe",
    f"http://api.telegram.org/bot{TOKEN}/getMe",  # Без HTTPS
    f"https://api.telegram.org/bot{TOKEN}/getUpdates",
]

for url in urls:
    print(f"\n🔗 Пробую: {url[:50]}...")
    
    try:
        # Отключаем SSL проверки для этого запроса
        response = requests.get(
            url, 
            timeout=30,
            verify=False,  # Отключаем SSL проверку
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        
        print(f"   Статус: {response.status_code}")
        print(f"   Ответ: {response.text[:100]}")
        
        if response.status_code == 200:
            print(f"   ✅ УСПЕХ!")
            break
            
    except requests.exceptions.SSLError as e:
        print(f"   ❌ SSL Ошибка: {e}")
    except Exception as e:
        print(f"   ❌ Ошибка: {type(e).__name__}: {str(e)[:50]}")

print("\n" + "=" * 60)
print("📋 Если ручные запросы работают, а бот нет -")
print("проблема в python-telegram-bot или httpx")
print("=" * 60)