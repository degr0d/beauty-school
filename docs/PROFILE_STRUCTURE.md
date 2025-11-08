# 📋 Структура работы профиля пользователя

## 🔄 Общий поток данных

```
[Браузер] → [Frontend React] → [API Client] → [Backend FastAPI] → [Database PostgreSQL]
     ↑                                                                    ↓
     └─────────────────────── [JSON Response] ─────────────────────────┘
```

---

## 1️⃣ Фронтенд (Frontend)

### 📁 Файл: `frontend/src/pages/ProfilePage.tsx`

**Что делает:**
- Отображает страницу профиля пользователя
- Загружает данные профиля при монтировании компонента
- Показывает ФИО, телефон, город, баллы, дату регистрации
- Загружает список купленных курсов с прогрессом

**Основные функции:**

#### `loadProfile()`
```typescript
1. Вызывает profileApi.get() → GET /api/profile
2. Получает rawProfile из ответа
3. Нормализует данные (преобразует все в примитивы):
   - created_at: datetime → string (ISO format)
   - Все поля проверяются на тип
   - Объекты преобразуются в строки (защита от React error #301)
4. Устанавливает профиль в state: setProfile(normalizedProfile)
5. Проверяет доступ: accessApi.checkAccess()
6. Устанавливает статус: 'loading' | 'not_registered' | 'not_paid' | 'paid'
```

#### `loadMyCourses()`
```typescript
1. Вызывается только если status === 'paid'
2. Вызывает coursesApi.getMyCourses() → GET /api/courses/my/courses
3. Нормализует данные курсов:
   - purchased_at: datetime → string
   - Все поля проверяются на тип
4. Устанавливает курсы в state: setMyCourses(courses)
```

**Состояния компонента:**
- `profile: Profile | null` - данные профиля
- `status: ProfileStatus` - статус ('loading' | 'not_registered' | 'not_paid' | 'paid')
- `myCourses: CourseWithProgress[]` - купленные курсы
- `loadingCourses: boolean` - загрузка курсов

---

## 2️⃣ API Client (Frontend)

### 📁 Файл: `frontend/src/api/client.ts`

**Что делает:**
- Настраивает Axios для всех API запросов
- Добавляет заголовки для аутентификации
- Обрабатывает ошибки

**Интерцептор запросов:**
```typescript
api.interceptors.request.use((config) => {
  // На localhost ВСЕГДА используем режим разработки
  if (isLocalhost) {
    const hasRealInitData = webApp?.initData && webApp.initData.trim().length > 0
    
    if (hasRealInitData) {
      // Реальный Telegram WebApp - используем initData
      config.headers['X-Telegram-Init-Data'] = webApp.initData
    } else {
      // РЕЖИМ РАЗРАБОТКИ: используем X-Telegram-User-ID
      const devTelegramId = localStorage.getItem('dev_telegram_id') || '123456789'
      config.headers['X-Telegram-User-ID'] = devTelegramId
    }
  } else {
    // Продакшен - используем initData
    if (webApp?.initData) {
      config.headers['X-Telegram-Init-Data'] = webApp.initData
    }
  }
  return config
})
```

**Profile API:**
```typescript
export const profileApi = {
  // Получить профиль
  get: () => api.get<Profile>('/profile'),
  
  // Обновить профиль
  update: (data: ProfileUpdateRequest) => 
    api.put<Profile>('/profile', data),
  
  // Получить список пользователей для разработки
  getDevUsers: () => 
    api.get<DevUsersResponse>('/profile/dev/users'),
}
```

**Интерфейс Profile:**
```typescript
export interface Profile {
  id: number
  telegram_id: number
  username?: string
  full_name: string
  phone: string
  city?: string
  points: number
  created_at: string  // ISO format string
}
```

---

## 3️⃣ Backend Route (FastAPI)

### 📁 Файл: `backend/webapp/routes/profile.py`

**Эндпоинт: `GET /api/profile`**

**Поток выполнения:**

#### Шаг 1: Dependency Injection
```python
async def get_profile(
    user: dict = Depends(get_telegram_user),  # ← Получаем данные пользователя
    session: AsyncSession = Depends(get_session)  # ← Получаем сессию БД
):
```

#### Шаг 2: Получение telegram_id
```python
telegram_id_raw = user["id"]  # Из middleware или заголовка X-Telegram-User-ID
telegram_id = int(telegram_id_raw)  # Преобразуем в int для БД
is_admin = telegram_id in settings.admin_ids_list
```

#### Шаг 3: Поиск пользователя в БД
```python
result = await session.execute(
    select(User).where(User.telegram_id == telegram_id)
)
db_user = result.scalar_one_or_none()
```

#### Шаг 4: Создание профиля (если не найден)
```python
if not db_user:
    # Автоматически создаем профиль для любого пользователя
    db_user = User(
        telegram_id=int(telegram_id),
        username=user.get("username"),
        full_name=f"{first_name} {last_name}".strip() or "Пользователь",
        phone="не указан",
        consent_personal_data=True,
        is_active=True,
        created_at=datetime.now()
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)
```

#### Шаг 5: Преобразование в Response
```python
# Преобразуем datetime в строку
if db_user.created_at is None:
    created_at_str = ""
elif hasattr(db_user.created_at, 'isoformat'):
    created_at_str = db_user.created_at.isoformat()
else:
    created_at_str = str(db_user.created_at)

# Создаем ProfileResponse
response = ProfileResponse(
    id=db_user.id,
    telegram_id=db_user.telegram_id,
    username=db_user.username,
    full_name=db_user.full_name,
    phone=db_user.phone,
    city=db_user.city,
    points=db_user.points,
    created_at=created_at_str  # ← Всегда строка!
)
return response
```

**Эндпоинт: `PUT /api/profile`**

```python
async def update_profile(
    profile_data: ProfileUpdateRequest,  # ← Данные для обновления
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    # Находим пользователя
    # Обновляем поля (если переданы)
    if profile_data.full_name:
        db_user.full_name = profile_data.full_name
    if profile_data.phone:
        db_user.phone = profile_data.phone
    if profile_data.city is not None:
        db_user.city = profile_data.city
    
    await session.commit()
    await session.refresh(db_user)
    
    # Возвращаем обновленный профиль
    return ProfileResponse(...)
```

---

## 4️⃣ Middleware (Аутентификация)

### 📁 Файл: `backend/webapp/middleware.py`

**Функция: `get_telegram_user(request: Request) -> dict`**

**Что делает:**
- Определяет пользователя из запроса
- В режиме разработки использует заголовок `X-Telegram-User-ID`
- В продакшене использует `X-Telegram-Init-Data` (валидирует через Telegram)

**Логика:**

```python
def get_telegram_user(request: Request) -> dict:
    # 1. Проверяем, установил ли middleware telegram_user
    if hasattr(request.state, "telegram_user"):
        return request.state.telegram_user
    
    # 2. РЕЖИМ РАЗРАБОТКИ (DEV_MODE=True)
    if settings.DEV_MODE and settings.ENVIRONMENT == "development":
        # Пробуем получить из заголовка X-Telegram-User-ID
        dev_telegram_id = request.headers.get("X-Telegram-User-ID")
        
        if dev_telegram_id:
            telegram_id = int(dev_telegram_id)
            return {
                "id": telegram_id,
                "first_name": "Dev",
                "last_name": "User",
                "username": "dev_user",
                "language_code": "ru"
            }
        
        # Или используем DEV_TELEGRAM_ID из настроек
        if settings.DEV_TELEGRAM_ID > 0:
            return {
                "id": settings.DEV_TELEGRAM_ID,
                ...
            }
    
    # 3. ПРОДАКШЕН: Валидация initData через Telegram
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        raise HTTPException(401, "Missing Telegram initData")
    
    # Валидируем через Telegram Bot API
    # Извлекаем данные пользователя
    # Возвращаем dict с данными пользователя
```

---

## 5️⃣ Схемы (Pydantic)

### 📁 Файл: `backend/webapp/schemas.py`

**ProfileResponse:**
```python
class ProfileResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    full_name: str
    phone: str
    city: Optional[str] = None
    points: int
    created_at: str  # ← Всегда строка (ISO format)
    
    class Config:
        from_attributes = True  # Позволяет создавать из ORM объектов
```

**ProfileUpdateRequest:**
```python
class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None
```

**Что делает:**
- Валидирует данные при получении/отправке
- Автоматически сериализует в JSON
- Преобразует ORM объекты в Pydantic модели

---

## 6️⃣ Модель БД (SQLAlchemy)

### 📁 Файл: `backend/database/models.py`

**Модель User:**
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    city = Column(String(100), nullable=True)
    consent_personal_data = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    points = Column(Integer, default=0, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_courses = relationship("UserCourse", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
```

**Что делает:**
- Определяет структуру таблицы `users` в PostgreSQL
- Создает связи с другими таблицами (user_courses, progress, achievements)
- Автоматически генерирует SQL запросы

---

## 7️⃣ База данных (PostgreSQL)

**Таблица: `users`**

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(100),
    consent_personal_data BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    points INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
```

---

## 🔄 Полный поток запроса профиля

### 1. Пользователь открывает страницу `/profile`

### 2. Frontend (ProfilePage.tsx)
```typescript
useEffect(() => {
  loadProfile()  // ← Вызывается при монтировании
}, [])
```

### 3. API Client (client.ts)
```typescript
profileApi.get()  // ← GET /api/profile
  ↓
api.get<Profile>('/profile')
  ↓
Axios добавляет заголовок:
  - На localhost: X-Telegram-User-ID: "310836227"
  - В продакшене: X-Telegram-Init-Data: "..."
```

### 4. Backend Route (profile.py)
```python
GET /api/profile
  ↓
get_profile(user=Depends(get_telegram_user), session=Depends(get_session))
  ↓
get_telegram_user() возвращает:
  {
    "id": 310836227,
    "first_name": "Dev",
    "last_name": "User",
    "username": "dev_user"
  }
  ↓
Поиск в БД: SELECT * FROM users WHERE telegram_id = 310836227
  ↓
Если найден → возвращаем ProfileResponse
Если не найден → создаем нового пользователя → возвращаем ProfileResponse
```

### 5. Response (JSON)
```json
{
  "id": 1,
  "telegram_id": 310836227,
  "username": "dev_user",
  "full_name": "Dev User",
  "phone": "не указан",
  "city": null,
  "points": 0,
  "created_at": "2025-11-08T18:30:36.123456"
}
```

### 6. Frontend обработка
```typescript
const rawProfile = profileResponse.data
  ↓
Нормализация данных (преобразование в примитивы)
  ↓
setProfile(normalizedProfile)
  ↓
Рендер компонента с данными профиля
```

---

## 🛡️ Защита от ошибок

### 1. React Error #301 (Objects are not valid as a React child)

**Проблема:** Backend может вернуть `datetime` объект вместо строки

**Решение в Frontend:**
```typescript
// Преобразуем created_at в строку
if (typeof rawProfile.created_at === 'object') {
  created_at_str = rawProfile.created_at.toISOString()
} else {
  created_at_str = String(rawProfile.created_at)
}

// Дополнительная проверка всех полей
for (const key of profileKeys) {
  const value = normalizedProfile[key]
  if (typeof value === 'object') {
    // Преобразуем объект в строку
    (normalizedProfile as any)[key] = JSON.stringify(value)
  }
}
```

**Решение в Backend:**
```python
# Всегда преобразуем datetime в строку
created_at_str = db_user.created_at.isoformat() if hasattr(db_user.created_at, 'isoformat') else str(db_user.created_at)

response = ProfileResponse(
    ...
    created_at=created_at_str  # ← Всегда строка!
)
```

### 2. Режим разработки (localhost)

**Проблема:** На localhost нет Telegram WebApp initData

**Решение:**
- Frontend отправляет заголовок `X-Telegram-User-ID`
- Backend в режиме разработки принимает этот заголовок
- Создает фейкового пользователя для разработки

---

## 📊 Структура данных

### Profile (Frontend TypeScript)
```typescript
interface Profile {
  id: number
  telegram_id: number
  username?: string
  full_name: string
  phone: string
  city?: string
  points: number
  created_at: string  // ISO format: "2025-11-08T18:30:36.123456"
}
```

### ProfileResponse (Backend Pydantic)
```python
class ProfileResponse(BaseModel):
    id: int
    telegram_id: int
    username: Optional[str] = None
    full_name: str
    phone: str
    city: Optional[str] = None
    points: int
    created_at: str  # ISO format string
```

### User (Backend SQLAlchemy)
```python
class User(Base):
    id: int
    telegram_id: int
    username: Optional[str]
    full_name: str
    phone: str
    city: Optional[str]
    points: int
    created_at: datetime  # ← Преобразуется в строку при сериализации
```

---

## 🔧 Режим разработки

### Как работает на localhost:

1. **Frontend** (`client.ts`):
   ```typescript
   if (isLocalhost) {
     const devTelegramId = localStorage.getItem('dev_telegram_id') || '123456789'
     config.headers['X-Telegram-User-ID'] = devTelegramId
   }
   ```

2. **Backend** (`middleware.py`):
   ```python
   if settings.DEV_MODE and settings.ENVIRONMENT == "development":
       dev_telegram_id = request.headers.get("X-Telegram-User-ID")
       if dev_telegram_id:
           return {
               "id": int(dev_telegram_id),
               "first_name": "Dev",
               "last_name": "User",
               "username": "dev_user"
           }
   ```

3. **Изменение ID:**
   - Через DevModeSelector компонент (UI)
   - Через консоль: `localStorage.setItem('dev_telegram_id', '310836227')`

---

## ✅ Итоговая схема

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  ProfilePage.tsx → loadProfile()                            │
│       ↓                                                      │
│  client.ts → profileApi.get()                               │
│       ↓                                                      │
│  Axios → GET /api/profile                                    │
│       + Header: X-Telegram-User-ID: "310836227"             │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP Request
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│  routes/profile.py → get_profile()                          │
│       ↓                                                      │
│  middleware.py → get_telegram_user()                        │
│       ↓ (возвращает dict с telegram_id)                      │
│  routes/profile.py → SELECT * FROM users WHERE ...           │
│       ↓                                                      │
│  schemas.py → ProfileResponse (Pydantic)                     │
│       ↓                                                      │
│  JSON Response                                               │
└─────────────────────────────────────────────────────────────┘
                            ↓ JSON
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                          │
│  Нормализация данных (все в примитивы)                      │
│       ↓                                                      │
│  setProfile(normalizedProfile)                              │
│       ↓                                                      │
│  Рендер компонента с данными                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Ключевые моменты

1. **Автоматическое создание профиля:** Если пользователя нет в БД, он создается автоматически
2. **Нормализация данных:** Все данные преобразуются в примитивы перед установкой в React state
3. **Режим разработки:** На localhost используется заголовок `X-Telegram-User-ID` вместо initData
4. **Типобезопасность:** TypeScript на фронтенде, Pydantic на бэкенде
5. **Защита от ошибок:** Множественные проверки типов и преобразования

