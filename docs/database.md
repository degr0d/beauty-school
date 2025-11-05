# 🗄️ Схема базы данных

## Обзор

База данных построена на **PostgreSQL** с использованием **SQLAlchemy ORM**.

---

## Таблицы

### 1. `users` — Пользователи

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | Внутренний ID | PRIMARY KEY |
| `telegram_id` | BIGINT | Telegram User ID | UNIQUE, NOT NULL |
| `username` | VARCHAR(255) | Telegram username | NULL |
| `full_name` | VARCHAR(255) | ФИО пользователя | NOT NULL |
| `phone` | VARCHAR(20) | Телефон | NOT NULL |
| `city` | VARCHAR(100) | Город (для рекомендаций чатов) | NULL |
| `consent_personal_data` | BOOLEAN | Согласие на обработку данных | DEFAULT FALSE |
| `is_active` | BOOLEAN | Активен ли пользователь | DEFAULT TRUE |
| `points` | INTEGER | Баллы (геймификация) | DEFAULT 0 |
| `created_at` | TIMESTAMP | Дата регистрации | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Последнее обновление | DEFAULT NOW() |

**Индексы:**
- `idx_telegram_id` на `telegram_id` (для быстрого поиска)

---

### 2. `courses` — Курсы

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID курса | PRIMARY KEY |
| `title` | VARCHAR(255) | Название курса | NOT NULL |
| `description` | TEXT | Описание (краткое) | NOT NULL |
| `full_description` | TEXT | Полное описание | NULL |
| `category` | VARCHAR(100) | Категория (маникюр, ресницы и т.д.) | NOT NULL |
| `cover_image_url` | TEXT | URL обложки | NULL |
| `is_top` | BOOLEAN | Топ курс месяца | DEFAULT FALSE |
| `price` | DECIMAL(10, 2) | Цена (для будущей оплаты) | DEFAULT 0 |
| `duration_hours` | INTEGER | Длительность в часах | NULL |
| `is_active` | BOOLEAN | Курс активен (виден пользователям) | DEFAULT TRUE |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | Последнее обновление | DEFAULT NOW() |

**Категории (примеры):**
- `manicure` — Маникюр
- `pedicure` — Педикюр
- `eyelashes` — Ресницы
- `podology` — Подология
- `eyebrows` — Брови
- `marketing` — Реклама/маркетинг
- `business` — Своё дело

---

### 3. `lessons` — Уроки

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID урока | PRIMARY KEY |
| `course_id` | INTEGER | ID курса | FOREIGN KEY -> courses(id), NOT NULL |
| `title` | VARCHAR(255) | Название урока | NOT NULL |
| `description` | TEXT | Описание урока | NULL |
| `order` | INTEGER | Порядковый номер в курсе | NOT NULL |
| `video_url` | TEXT | URL видео | NULL |
| `video_duration` | INTEGER | Длительность видео (секунды) | NULL |
| `pdf_url` | TEXT | URL PDF/чек-листа | NULL |
| `is_free` | BOOLEAN | Бесплатный урок (для превью) | DEFAULT FALSE |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Индексы:**
- `idx_course_order` на `(course_id, order)` (для быстрой сортировки)

---

### 4. `user_courses` — Доступ пользователей к курсам

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID записи | PRIMARY KEY |
| `user_id` | INTEGER | ID пользователя | FOREIGN KEY -> users(id), NOT NULL |
| `course_id` | INTEGER | ID курса | FOREIGN KEY -> courses(id), NOT NULL |
| `purchased_at` | TIMESTAMP | Когда получил доступ | DEFAULT NOW() |
| `completed_at` | TIMESTAMP | Когда завершил курс | NULL |
| `is_completed` | BOOLEAN | Курс завершён | DEFAULT FALSE |

**Уникальность:**
- `UNIQUE(user_id, course_id)` — один пользователь не может "купить" курс дважды

---

### 5. `user_progress` — Прогресс по урокам

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID записи | PRIMARY KEY |
| `user_id` | INTEGER | ID пользователя | FOREIGN KEY -> users(id), NOT NULL |
| `lesson_id` | INTEGER | ID урока | FOREIGN KEY -> lessons(id), NOT NULL |
| `completed` | BOOLEAN | Урок завершён | DEFAULT FALSE |
| `completed_at` | TIMESTAMP | Когда завершён | NULL |
| `watch_time` | INTEGER | Время просмотра (секунды) | DEFAULT 0 |

**Уникальность:**
- `UNIQUE(user_id, lesson_id)` — один прогресс на урок на пользователя

---

### 6. `achievements` — Достижения (ачивки)

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID ачивки | PRIMARY KEY |
| `title` | VARCHAR(255) | Название | NOT NULL |
| `description` | TEXT | Описание | NOT NULL |
| `icon_url` | TEXT | URL иконки | NULL |
| `points` | INTEGER | Баллы за получение | DEFAULT 0 |
| `condition_type` | VARCHAR(50) | Тип условия (courses_completed, etc.) | NOT NULL |
| `condition_value` | INTEGER | Значение условия (например, 3 курса) | NOT NULL |

**Примеры ачивок:**
- `Первый курс завершён` — condition_type: `courses_completed`, condition_value: `1`
- `Мастер ногтей` — condition_type: `category_courses_completed`, condition_value: `3` (+ category: `manicure`)

---

### 7. `user_achievements` — Полученные ачивки

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID записи | PRIMARY KEY |
| `user_id` | INTEGER | ID пользователя | FOREIGN KEY -> users(id), NOT NULL |
| `achievement_id` | INTEGER | ID ачивки | FOREIGN KEY -> achievements(id), NOT NULL |
| `earned_at` | TIMESTAMP | Когда получена | DEFAULT NOW() |

**Уникальность:**
- `UNIQUE(user_id, achievement_id)` — одну ачивку нельзя получить дважды

---

### 8. `communities` — Сообщества/чаты (опционально)

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID сообщества | PRIMARY KEY |
| `title` | VARCHAR(255) | Название чата | NOT NULL |
| `description` | TEXT | Описание | NULL |
| `type` | VARCHAR(50) | Тип: `city` или `profession` | NOT NULL |
| `city` | VARCHAR(100) | Город (если type=city) | NULL |
| `category` | VARCHAR(100) | Категория профессии (если type=profession) | NULL |
| `telegram_link` | TEXT | Ссылка на Telegram-чат | NOT NULL |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |

**Примеры:**
- Тип `city`: "Мастера Москвы"
- Тип `profession`: "Ресницы" (все мастера по ресницам)

---

### 9. `payments` — Платежи (для будущей интеграции)

| Колонка | Тип | Описание | Ограничения |
|---------|-----|----------|-------------|
| `id` | SERIAL | ID платежа | PRIMARY KEY |
| `user_id` | INTEGER | ID пользователя | FOREIGN KEY -> users(id), NOT NULL |
| `course_id` | INTEGER | ID курса | FOREIGN KEY -> courses(id), NOT NULL |
| `amount` | DECIMAL(10, 2) | Сумма платежа | NOT NULL |
| `currency` | VARCHAR(3) | Валюта (RUB, USD) | DEFAULT 'RUB' |
| `status` | VARCHAR(50) | Статус: pending, succeeded, failed | DEFAULT 'pending' |
| `payment_method` | VARCHAR(50) | Метод оплаты (yukassa) | NULL |
| `external_id` | VARCHAR(255) | ID платежа в ЮKassa | NULL |
| `created_at` | TIMESTAMP | Дата создания | DEFAULT NOW() |
| `paid_at` | TIMESTAMP | Дата успешной оплаты | NULL |

---

## Связи между таблицами

```
users (1) ──< (N) user_courses (N) >── (1) courses
                                              │
                                              │
                                              ▼
                                          lessons (N)
                                              │
                                              │
                                              ▼
users (1) ──< (N) user_progress (N) >── (1) lessons

users (1) ──< (N) user_achievements (N) >── (1) achievements

users (1) ──< (N) payments (N) >── (1) courses
```

---

## Примеры SQL-запросов

### 1. Получить все курсы пользователя с прогрессом

```sql
SELECT 
    c.id,
    c.title,
    c.category,
    uc.purchased_at,
    uc.is_completed,
    COUNT(l.id) as total_lessons,
    COUNT(CASE WHEN up.completed = TRUE THEN 1 END) as completed_lessons,
    ROUND(
        COUNT(CASE WHEN up.completed = TRUE THEN 1 END)::NUMERIC / COUNT(l.id) * 100
    ) as progress_percent
FROM user_courses uc
JOIN courses c ON c.id = uc.course_id
JOIN lessons l ON l.course_id = c.id
LEFT JOIN user_progress up ON up.lesson_id = l.id AND up.user_id = uc.user_id
WHERE uc.user_id = 123
GROUP BY c.id, c.title, c.category, uc.purchased_at, uc.is_completed;
```

### 2. Топ-5 самых популярных курсов

```sql
SELECT 
    c.id,
    c.title,
    COUNT(uc.user_id) as students_count
FROM courses c
LEFT JOIN user_courses uc ON uc.course_id = c.id
GROUP BY c.id, c.title
ORDER BY students_count DESC
LIMIT 5;
```

### 3. Пользователи, которые не завершили ни одного урока за последние 7 дней

```sql
SELECT DISTINCT u.id, u.full_name, u.telegram_id
FROM users u
JOIN user_courses uc ON uc.user_id = u.id
LEFT JOIN user_progress up ON up.user_id = u.id 
    AND up.completed = TRUE 
    AND up.completed_at >= NOW() - INTERVAL '7 days'
WHERE up.id IS NULL
  AND uc.is_completed = FALSE;
```

---

## Миграции (Alembic)

### Инициализация

```bash
# Создание папки миграций
alembic init backend/database/migrations

# Настройка alembic.ini (указать sqlalchemy.url)

# Создание первой миграции
alembic revision --autogenerate -m "Initial schema"

# Применение миграций
alembic upgrade head
```

### Пример миграции (добавить колонку `city` в `users`)

```bash
alembic revision -m "Add city to users"
```

Файл миграции:
```python
def upgrade():
    op.add_column('users', sa.Column('city', sa.String(100), nullable=True))

def downgrade():
    op.drop_column('users', 'city')
```

---

## Бэкапы

### Для разработки

```bash
# Дамп БД
docker-compose exec postgres pg_dump -U beauty_user beauty_db > backup.sql

# Восстановление
docker-compose exec -T postgres psql -U beauty_user beauty_db < backup.sql
```

### Для продакшена

- Автоматические бэкапы через cron (ежедневно)
- Хранение на S3/облаке
- Retention policy: последние 30 дней

---

## Оптимизация

### Индексы (добавить при росте нагрузки)

```sql
-- Быстрый поиск пользователя по telegram_id
CREATE INDEX idx_users_telegram_id ON users(telegram_id);

-- Быстрая сортировка уроков
CREATE INDEX idx_lessons_course_order ON lessons(course_id, order);

-- Быстрый подсчёт прогресса
CREATE INDEX idx_user_progress_user_lesson ON user_progress(user_id, lesson_id);
```

### Партиционирование (для будущего)

Если таблица `user_progress` станет огромной, можно партиционировать по `user_id` или дате.

---

## Итоги

Эта схема БД покрывает:
✅ Пользователей и регистрацию
✅ Курсы и уроки
✅ Прогресс и доступ
✅ Геймификацию (ачивки, баллы)
✅ Платежи (для будущей интеграции)
✅ Сообщества

Следующий шаг: **план разработки MVP** → `mvp-roadmap.md`

