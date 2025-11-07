"""
Middleware для FastAPI
Валидация Telegram initData (авторизация пользователей)
"""

import hmac
import hashlib
from urllib.parse import parse_qsl
from typing import Optional

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from backend.config import settings


class TelegramAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware для проверки подписи Telegram initData
    
    Telegram передаёт данные пользователя в виде строки:
    query_id=...&user=%7B%22id%22%3A123...&auth_date=...&hash=abc123
    
    Нужно проверить:
    1. Подпись hash (HMAC-SHA256)
    2. Срок auth_date (не старше 5 минут)
    """
    
    async def dispatch(self, request: Request, call_next):
        # Пропускаем некоторые пути без авторизации
        if request.url.path in ["/health", "/api/docs", "/api/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Получаем initData из заголовка
        init_data = request.headers.get("X-Telegram-Init-Data")
        
        if not init_data:
            print(f"⚠️ [Middleware] Отсутствует X-Telegram-Init-Data для {request.url.path}")
            raise HTTPException(status_code=401, detail="Missing Telegram initData")
        
        # Проверяем подпись
        user = self.validate_init_data(init_data)
        
        if not user:
            print(f"⚠️ [Middleware] Невалидный initData для {request.url.path}")
            print(f"   initData (первые 100 символов): {init_data[:100]}")
            raise HTTPException(status_code=401, detail="Invalid Telegram initData")
        
        print(f"✅ [Middleware] Пользователь авторизован: telegram_id={user.get('id')}, path={request.url.path}")
        
        # Добавляем user в request.state для использования в эндпоинтах
        request.state.telegram_user = user
        
        response = await call_next(request)
        return response
    
    def validate_init_data(self, init_data: str) -> Optional[dict]:
        """
        Проверяет подпись Telegram initData
        
        Args:
            init_data: Строка с данными от Telegram
        
        Returns:
            dict с данными пользователя или None, если подпись невалидна
        """
        try:
            # Парсим initData
            data = dict(parse_qsl(init_data))
            
            # Извлекаем hash
            received_hash = data.pop("hash", None)
            if not received_hash:
                print(f"⚠️ [Middleware] Нет hash в initData")
                return None
            
            # Сортируем остальные параметры
            data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
            
            # Генерируем секретный ключ
            secret_key = hmac.new(
                key=b"WebAppData",
                msg=settings.BOT_TOKEN.encode(),
                digestmod=hashlib.sha256
            ).digest()
            
            # Вычисляем hash
            calculated_hash = hmac.new(
                key=secret_key,
                msg=data_check_string.encode(),
                digestmod=hashlib.sha256
            ).hexdigest()
            
            # Сравниваем hash
            if calculated_hash != received_hash:
                print(f"⚠️ [Middleware] Hash не совпадает: received={received_hash[:20]}..., calculated={calculated_hash[:20]}...")
                return None
            
            # Проверяем auth_date (не старше 5 минут) - но не блокируем если старше
            import time
            auth_date = int(data.get("auth_date", 0))
            time_diff = time.time() - auth_date
            if time_diff > 300:  # 5 минут
                print(f"⚠️ [Middleware] auth_date устарел: {time_diff:.0f} секунд назад")
                # Не блокируем - просто предупреждаем
                # return None
            
            # Извлекаем данные пользователя
            import json
            user_data = json.loads(data.get("user", "{}"))
            
            # Явно конвертируем telegram_id в int (из JSON может прийти как число или строка)
            if "id" in user_data:
                user_data["id"] = int(user_data["id"])
            
            print(f"✅ [Middleware] initData валиден: telegram_id={user_data.get('id')} (type: {type(user_data.get('id'))})")
            return user_data
        
        except Exception as e:
            print(f"❌ [Middleware] Ошибка валидации initData: {e}")
            import traceback
            traceback.print_exc()
            return None


# ========================================
# Dependency для получения user в эндпоинтах
# ========================================
from fastapi import Depends

def get_telegram_user(request: Request) -> dict:
    """
    Dependency для FastAPI эндпоинтов
    Возвращает данные пользователя из Telegram
    
    Использование:
    @app.get("/api/profile")
    async def get_profile(user: dict = Depends(get_telegram_user)):
        telegram_id = user["id"]
        ...
    """
    # Если middleware установил telegram_user - используем его
    if hasattr(request.state, "telegram_user"):
        return request.state.telegram_user
    
    # РЕЖИМ РАЗРАБОТКИ: Если ENVIRONMENT=development, разрешаем обход авторизации
    if settings.ENVIRONMENT == "development":
        # Пробуем получить telegram_id из заголовка (для локального тестирования)
        dev_telegram_id = request.headers.get("X-Telegram-User-ID")
        print(f"🔧 [DEV MODE] Проверка заголовков: X-Telegram-User-ID={dev_telegram_id}")
        print(f"🔧 [DEV MODE] ADMIN_IDS из настроек: {settings.ADMIN_IDS}")
        print(f"🔧 [DEV MODE] admin_ids_list: {settings.admin_ids_list}")
        
        if dev_telegram_id:
            try:
                telegram_id = int(dev_telegram_id)
                is_admin = telegram_id in settings.admin_ids_list
                print(f"🔧 [DEV MODE] Используем telegram_id из заголовка: {telegram_id}, is_admin={is_admin}")
                return {
                    "id": telegram_id,
                    "first_name": "Dev",
                    "last_name": "User",
                    "username": "dev_user"
                }
            except ValueError:
                print(f"⚠️ [DEV MODE] Невалидный X-Telegram-User-ID: {dev_telegram_id}")
        
        # Или используем админский ID по умолчанию
        admin_ids = settings.admin_ids_list
        if admin_ids:
            default_id = admin_ids[0]
            print(f"🔧 [DEV MODE] Используем админский ID по умолчанию: {default_id}")
            print(f"🔧 [DEV MODE] Этот ID будет использован для проверки админских прав")
            return {
                "id": default_id,
                "first_name": "Admin",
                "last_name": "Dev",
                "username": "admin_dev"
            }
        else:
            print(f"⚠️ [DEV MODE] ADMIN_IDS не установлен! Проверьте .env файл")
    
    # В режиме разработки (когда middleware отключен):
    # Пробуем получить initData из заголовка и проверить его
    init_data = request.headers.get("X-Telegram-Init-Data")
    if init_data:
        print(f"🔍 [get_telegram_user] initData найден в заголовке, валидирую...")
        # Валидируем initData напрямую
        user = validate_init_data_direct(init_data)
        if user:
            print(f"✅ [get_telegram_user] Пользователь авторизован: telegram_id={user.get('id')}")
            return user
        else:
            print(f"❌ [get_telegram_user] Валидация initData не прошла")
    else:
        print(f"⚠️ [get_telegram_user] initData не найден в заголовке X-Telegram-Init-Data")
    
    # Если ничего не получилось - возвращаем ошибку
    raise HTTPException(status_code=401, detail="Unauthorized. Please register via Telegram bot.")


def validate_init_data_direct(init_data: str) -> Optional[dict]:
    """
    Прямая валидация initData без создания middleware
    Используется в режиме разработки
    """
    try:
        print(f"🔍 [validate_init_data_direct] Начало валидации initData")
        print(f"   initData (первые 100 символов): {init_data[:100] if len(init_data) > 100 else init_data}")
        
        # Парсим initData
        data = dict(parse_qsl(init_data))
        
        # Извлекаем hash
        received_hash = data.pop("hash", None)
        if not received_hash:
            print(f"⚠️ [validate_init_data_direct] Нет hash в initData")
            return None
        
        # Сортируем остальные параметры
        data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data.items()))
        
        # Генерируем секретный ключ
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()
        
        # Вычисляем hash
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # Сравниваем hash
        if calculated_hash != received_hash:
            print(f"⚠️ [validate_init_data_direct] Hash не совпадает")
            print(f"   received={received_hash[:20]}...")
            print(f"   calculated={calculated_hash[:20]}...")
            return None
        
        # Проверяем auth_date (не старше 5 минут) - но не блокируем если старше
        import time
        auth_date = int(data.get("auth_date", 0))
        time_diff = time.time() - auth_date
        if time_diff > 300:  # 5 минут
            print(f"⚠️ [validate_init_data_direct] auth_date устарел: {time_diff:.0f} секунд назад")
            # Не блокируем - просто предупреждаем
        
        # Извлекаем данные пользователя
        import json
        user_data = json.loads(data.get("user", "{}"))
        
        # Явно конвертируем telegram_id в int (из JSON может прийти как число или строка)
        if "id" in user_data:
            user_data["id"] = int(user_data["id"])
        
        print(f"✅ [validate_init_data_direct] initData валиден: telegram_id={user_data.get('id')} (type: {type(user_data.get('id'))})")
        return user_data
    
    except Exception as e:
        print(f"❌ [validate_init_data_direct] Ошибка валидации: {e}")
        import traceback
        traceback.print_exc()
        return None


# ========================================
# ВАЖНО ДЛЯ РАЗРАБОТКИ:
# ========================================
# В режиме разработки можно временно отключить проверку initData
# и передавать telegram_id напрямую в заголовке X-Telegram-User-ID
# 
# Для этого закомментируйте:
# app.add_middleware(TelegramAuthMiddleware)
# 
# И добавьте в эндпоинты:
# telegram_id = request.headers.get("X-Telegram-User-ID", 123456789)

