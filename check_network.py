# check_network.py
import requests
import socket
import yaml
from datetime import datetime

print("=" * 70)
print("🔍 ДИАГНОСТИКА СЕТИ И ТОКЕНА")
print("=" * 70)

# 1. Читаем токен
try:
    with open('config.yaml', 'r', encoding='utf-8-sig') as f:
        config = yaml.safe_load(f)
    TOKEN = config['telegram']['token']
    print(f"✅ Токен прочитан: {TOKEN[:15]}...")
except Exception as e:
    print(f"❌ Ошибка чтения config.yaml: {e}")
    exit(1)

# 2. Проверяем интернет
print("\n🌐 Проверка интернета:")
try:
    resp = requests.get("https://google.com", timeout=5)
    print(f"   ✅ Интернет работает (статус: {resp.status_code})")
except:
    print("   ❌ Нет интернета!")
    print("   Проверьте: VPN, прокси, антивирус, брандмауэр")

# 3. Проверяем DNS
print("\n🔤 Проверка DNS:")
try:
    ip = socket.gethostbyname('api.telegram.org')
    print(f"   ✅ DNS разрешен: api.telegram.org -> {ip}")
except socket.gaierror:
    print("   ❌ DNS ошибка! Не могу разрешить api.telegram.org")
    print("   Попробуйте: ipconfig /flushdns")

# 4. Проверяем подключение к Telegram API
print("\n🤖 Проверка Telegram API:")
telegram_urls = [
    "https://api.telegram.org",
    "http://api.telegram.org",  # Без HTTPS
    "https://api.telegram.org/bot" + TOKEN + "/getMe"
]

for url in telegram_urls:
    try:
        start_time = datetime.now()
        resp = requests.get(url, timeout=10, verify=False)
        end_time = datetime.now()
        ms = (end_time - start_time).total_seconds() * 1000
        
        if resp.status_code == 200:
            print(f"   ✅ {url[:40]}... - OK ({ms:.0f} мс)")
        else:
            print(f"   ⚠ {url[:40]}... - статус {resp.status_code} ({ms:.0f} мс)")
    except requests.exceptions.SSLError:
        print(f"   🔒 SSL ошибка на {url[:40]}...")
    except requests.exceptions.ConnectTimeout:
        print(f"   ⏱ ТАЙМАУТ на {url[:40]}...")
    except Exception as e:
        print(f"   ❌ {url[:40]}... - {type(e).__name__}: {str(e)[:50]}")

# 5. Проверка токена
print("\n🔑 Проверка токена через API:")
try:
    resp = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=15)
    print(f"   Статус: {resp.status_code}")
    
    if resp.status_code == 200:
        data = resp.json()
        if data.get('ok'):
            bot = data['result']
            print(f"   ✅ ТОКЕН РАБОЧИЙ!")
            print(f"   Бот: {bot.get('first_name')} (@{bot.get('username')})")
        else:
            print(f"   ❌ Токен неверный: {data.get('description')}")
    elif resp.status_code == 403:
        print("   ❌ Токен заблокирован или неверный")
    else:
        print(f"   ⚠ Неожиданный статус: {resp.status_code}")
except Exception as e:
    print(f"   ❌ Ошибка запроса: {type(e).__name__}")

print("\n" + "=" * 70)
print("📋 РЕКОМЕНДАЦИИ:")
print("1. Если есть VPN - отключите его временно")
print("2. Проверьте настройки брандмауэра Windows")
print("3. Попробуйте запустить от имени администратора")
print("4. Проверьте, не блокирует ли антивирус")
print("=" * 70)