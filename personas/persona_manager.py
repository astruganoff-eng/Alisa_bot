import random
from typing import Dict, Optional, Any
import yaml
import requests

class PersonaManager:
    """Управляет персонажами и переключением между ними"""
    
    def __init__(self):
        self.personas = {}
        self.active_personas = {}  # user_id -> persona_name
        self.conversation_history = {}  # user_id -> list[dict]
        
        # Импортируем персонажей
        from .mark_male import MarkPersona
        from .alisa_female import AlisaPersona
        
        self.personas = {
            "mark": MarkPersona(),
            "alisa": AlisaPersona()
        }
        
        print(f"✅ Загружено персонажей: {list(self.personas.keys())}")
    
    def set_active_persona(self, user_id: int, persona_name: str) -> bool:
        """Устанавливает активного персонажа для пользователя"""
        if persona_name not in self.personas:
            return False
        
        self.active_personas[user_id] = persona_name
        
        # Инициализируем историю диалога
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        # Добавляем системное сообщение в историю
        persona = self.personas[persona_name]
        self.conversation_history[user_id].append({
            "role": "system",
            "content": persona.system_prompt
        })
        
        return True
    
    def get_active_persona(self, user_id: int):
        """Возвращает активного персонажа для пользователя"""
        if user_id not in self.active_personas:
            return None
        return self.personas[self.active_personas[user_id]]
    
    def get_persona_info(self, user_id: int) -> Dict[str, Any]:
        """Информация о текущем персонаже"""
        persona = self.get_active_persona(user_id)
        if not persona:
            return {"error": "Персонаж не выбран"}
        
        return {
            "name": persona.name,
            "gender": persona.gender,
            "age": persona.age,
            "persona_key": self.active_personas[user_id]
        }
    
    def add_user_message(self, user_id: int, message: str):
        """Добавляет сообщение пользователя в историю"""
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        
        self.conversation_history[user_id].append({
            "role": "user",
            "content": message
        })
        
        # Ограничиваем историю последними 10 сообщениями
        if len(self.conversation_history[user_id]) > 20:
            self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
    
    def generate_response(self, user_id: int, message: str, use_lmstudio: bool = True) -> str:
        """Генерирует ответ от активного персонажа"""
        persona = self.get_active_persona(user_id)
        if not persona:
            return "Сначала выбери персонажа командой /mark или /alisa"
        
        # Добавляем сообщение в историю
        self.add_user_message(user_id, message)
        
        if use_lmstudio:
            # Генерация через LM Studio
            return self._generate_via_lmstudio(user_id, persona)
        else:
            # Простой ответ (заглушка)
            return self._generate_fallback(persona)
    
    def _generate_via_lmstudio(self, user_id: int, persona) -> str:
        """Генерация через LM Studio API"""
        try:
            # Читаем конфиг
            with open('config.yaml', 'r', encoding='utf-8-sig') as f:
                config = yaml.safe_load(f)
            
            lmstudio_config = config.get('lmstudio', {})
            api_url = lmstudio_config.get('api_url', 'http://127.0.0.1:1234')
            
            # Подготавливаем промпт с историей
            messages = self.conversation_history[user_id][-6:]  # Берем последние 6 сообщений
            
            payload = {
                "messages": messages,
                "max_tokens": lmstudio_config.get('max_tokens', 150),
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                f"{api_url}/v1/chat/completions",
                json=payload,
                timeout=lmstudio_config.get('timeout', 15)
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result['choices'][0]['message']['content']
                
                # Добавляем ответ в историю
                self.conversation_history[user_id].append({
                    "role": "assistant",
                    "content": reply
                })
                
                return reply
            else:
                return self._generate_fallback(persona)
                
        except Exception as e:
            print(f"❌ Ошибка LM Studio: {e}")
            return self._generate_fallback(persona)
    
    def _generate_fallback(self, persona) -> str:
        """Запасной ответ из списка"""
        return random.choice(persona.fallback_responses)
    
    def get_available_personas(self) -> list:
        """Список доступных персонажей"""
        return [
            {"key": "mark", "name": "Марк", "gender": "male", "age": 28},
            {"key": "alisa", "name": "Алиса", "gender": "female", "age": 25}
        ]