"""
API эндпоинты для профиля пользователя
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database import get_session, User
from backend.webapp.schemas import ProfileResponse, ProfileUpdateRequest
from backend.webapp.middleware import get_telegram_user
from backend.config import settings

router = APIRouter()


@router.get("", response_model=ProfileResponse)
@router.get("/", response_model=ProfileResponse)
async def get_profile(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить профиль текущего пользователя
    
    Автоматически создает профиль для любого пользователя, если его нет в БД
    """
    print("🚀 [Profile] ФУНКЦИЯ get_profile ВЫЗВАНА!")
    print(f"   Session type: {type(session)}")
    print(f"   Session: {session}")
    try:
        # Явно преобразуем telegram_id в int для корректного сравнения с БД
        telegram_id_raw = user["id"]
        telegram_id = int(telegram_id_raw) if telegram_id_raw is not None else None
        
        if telegram_id is None:
            print(f"❌ [Profile] telegram_id отсутствует в данных пользователя")
            raise HTTPException(status_code=400, detail="Missing telegram_id in user data")
        
        is_admin = telegram_id in settings.admin_ids_list
        
        print(f"🔍 [Profile] Запрос профиля для telegram_id={telegram_id} (type: {type(telegram_id)}, raw: {telegram_id_raw}, raw_type: {type(telegram_id_raw)}), is_admin={is_admin}")
        print(f"   Данные из Telegram: username={user.get('username')}, first_name={user.get('first_name')}, last_name={user.get('last_name')}")
        print(f"   Session closed: {session.is_closed if hasattr(session, 'is_closed') else 'unknown'}")
        
        # Ищем пользователя по telegram_id (BIGINT в БД)
        print(f"   Выполняю запрос к БД...")
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        db_user = result.scalar_one_or_none()
        print(f"   Результат запроса: {db_user}")
        
        if db_user:
            print(f"✅ [Profile] Пользователь найден: telegram_id={db_user.telegram_id} (type: {type(db_user.telegram_id)})")
        
        if not db_user:
            # Если пользователя нет в БД - создаем профиль автоматически для любого пользователя
            print(f"👤 [Profile] Пользователь не найден в БД, создаем профиль автоматически")
            print(f"   telegram_id={telegram_id} не найден среди зарегистрированных")
            
            # Получаем данные из Telegram
            username = user.get("username")
            first_name = user.get("first_name", "")
            last_name = user.get("last_name", "")
            full_name = f"{first_name} {last_name}".strip() or ("Администратор" if is_admin else "Пользователь")
            
            # Создаем пользователя - гарантируем что telegram_id это int
            from datetime import datetime
            db_user = User(
                telegram_id=int(telegram_id),  # Явно преобразуем в int
                username=username,
                full_name=full_name,
                phone="не указан",  # Пользователь может указать позже через редактирование профиля
                consent_personal_data=True,
                is_active=True,
                created_at=datetime.now()  # Явно устанавливаем created_at
            )
            session.add(db_user)
            await session.commit()
            await session.refresh(db_user)
            
            print(f"✅ [Profile] Профиль создан: {db_user.full_name} (telegram_id={db_user.telegram_id}, id={db_user.id}, is_admin={is_admin})")
            print(f"   Данные после создания: full_name={db_user.full_name}, phone={db_user.phone}, username={db_user.username}")
            
            # Безопасно получаем email (на случай если миграция не применена)
            try:
                email = db_user.email
            except AttributeError:
                email = None
                print(f"⚠️ [Profile] Поле email не найдено в модели (миграция не применена)")
            
            profile_data = {
                "id": db_user.id,
                "telegram_id": db_user.telegram_id,
                "username": db_user.username,
                "full_name": db_user.full_name,
                "phone": db_user.phone,
                "email": email,
                "city": db_user.city,
                "points": db_user.points,
                "created_at": db_user.created_at
            }
            print(f"📤 [Profile] Возвращаю данные нового профиля: {profile_data}")
            
            # Преобразуем datetime в строку для корректной JSON сериализации
            try:
                if db_user.created_at is None:
                    created_at_str = ""
                elif hasattr(db_user.created_at, 'isoformat'):
                    created_at_str = db_user.created_at.isoformat()
                else:
                    created_at_str = str(db_user.created_at)
            except Exception as e:
                print(f"⚠️ [Profile] Ошибка преобразования created_at: {e}")
                from datetime import datetime
                created_at_str = datetime.now().isoformat()
            
            response = ProfileResponse(
                id=db_user.id,
                telegram_id=db_user.telegram_id,
                username=db_user.username,
                full_name=db_user.full_name,
                phone=db_user.phone,
                email=email,
                city=db_user.city,
                points=db_user.points,
                created_at=created_at_str
            )
            
            print(f"📤 [Profile] ProfileResponse создан для нового пользователя: full_name={response.full_name}, phone={response.phone}")
            return response
        else:
            print(f"✅ [Profile] Профиль найден: {db_user.full_name} (telegram_id={db_user.telegram_id}, id={db_user.id}, phone={db_user.phone})")
        
        # Безопасно получаем email (на случай если миграция не применена)
        try:
            email = db_user.email
        except AttributeError:
            email = None
            print(f"⚠️ [Profile] Поле email не найдено в модели (миграция не применена)")
        
        # Логируем все данные перед возвратом
        profile_data = {
            "id": db_user.id,
            "telegram_id": db_user.telegram_id,
            "username": db_user.username,
            "full_name": db_user.full_name,
            "phone": db_user.phone,
            "email": email,
            "city": db_user.city,
            "points": db_user.points,
            "created_at": db_user.created_at
        }
        print(f"📤 [Profile] Возвращаю данные профиля: {profile_data}")
        
        # Преобразуем datetime в строку для корректной JSON сериализации
        try:
            if db_user.created_at is None:
                created_at_str = ""
            elif hasattr(db_user.created_at, 'isoformat'):
                created_at_str = db_user.created_at.isoformat()
            else:
                created_at_str = str(db_user.created_at)
        except Exception as e:
            print(f"⚠️ [Profile] Ошибка преобразования created_at: {e}")
            from datetime import datetime
            created_at_str = datetime.now().isoformat()
        
        response = ProfileResponse(
            id=db_user.id,
            telegram_id=db_user.telegram_id,
            username=db_user.username,
            full_name=db_user.full_name,
            phone=db_user.phone,
            email=email,
            city=db_user.city,
            points=db_user.points,
            created_at=created_at_str
        )
        
        print(f"📤 [Profile] ProfileResponse создан: full_name={response.full_name}, phone={response.phone}, email={response.email}, city={response.city}")
        return response
    except Exception as e:
        print(f"❌ [Profile] ОШИБКА при получении профиля: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/", response_model=ProfileResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Обновить профиль пользователя
    """
    # Явно преобразуем telegram_id в int
    telegram_id_raw = user["id"]
    telegram_id = int(telegram_id_raw) if telegram_id_raw is not None else None
    
    if telegram_id is None:
        raise HTTPException(status_code=400, detail="Missing telegram_id in user data")
    
    # Ищем пользователя по telegram_id
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Обновляем поля
    if profile_data.full_name:
        db_user.full_name = profile_data.full_name
    if profile_data.phone:
        db_user.phone = profile_data.phone
    if profile_data.email is not None:  # Разрешаем пустую строку для очистки email
        db_user.email = profile_data.email
    if profile_data.city is not None:  # Разрешаем пустую строку для очистки city
        db_user.city = profile_data.city
    
    await session.commit()
    await session.refresh(db_user)
    
    # Безопасно получаем email (на случай если миграция не применена)
    try:
        email = db_user.email
    except AttributeError:
        email = None
    
    # Преобразуем datetime в строку для корректной JSON сериализации
    try:
        if db_user.created_at is None:
            created_at_str = ""
        elif hasattr(db_user.created_at, 'isoformat'):
            created_at_str = db_user.created_at.isoformat()
        else:
            created_at_str = str(db_user.created_at)
    except Exception as e:
        print(f"⚠️ [Profile] Ошибка преобразования created_at: {e}")
        from datetime import datetime
        created_at_str = datetime.now().isoformat()
    
    return ProfileResponse(
        id=db_user.id,
        telegram_id=db_user.telegram_id,
        username=db_user.username,
        full_name=db_user.full_name,
        phone=db_user.phone,
        email=email,
        city=db_user.city,
        points=db_user.points,
        created_at=created_at_str
    )


# ========================================
# Пример запроса:
# ========================================
# GET /api/profile
# PUT /api/profile
# Body: {"full_name": "Иванова Мария", "city": "Москва"}

