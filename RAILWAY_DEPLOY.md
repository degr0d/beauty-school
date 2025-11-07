# 🚂 Деплой Backend на Railway

## Быстрый старт

### 1. Установите Railway CLI

```bash
# macOS
brew install railway

# Или через npm
npm i -g @railway/cli
```

### 2. Войдите в Railway

```bash
railway login
```

### 3. Создайте проект

```bash
railway init
```

Следуйте инструкциям:
- Выберите "Create new project"
- Назовите проект: `beauty-school-backend`

### 4. Добавьте PostgreSQL базу данных

```bash
railway add postgresql
```

Railway автоматически создаст переменную `DATABASE_URL`.

### 5. Добавьте переменные окружения

```bash
# Откройте веб-интерфейс Railway
railway variables

# Или через CLI:
railway variables set BOT_TOKEN=your_bot_token
railway variables set ADMIN_BOT_TOKEN=your_admin_bot_token
railway variables set ADMIN_IDS=your_telegram_id
railway variables set ENVIRONMENT=production
railway variables set FRONTEND_URL=https://beauty-school-two.vercel.app
railway variables set WEBAPP_URL=https://beauty-school-two.vercel.app
railway variables set SECRET_KEY=your_secret_key_here
```

**Важно:** Railway автоматически добавит `DATABASE_URL` после создания PostgreSQL.

### 6. Создайте два сервиса

**Важно:** Railway нужно создать ДВА сервиса:
1. **API сервис** (для FastAPI)
2. **Bot сервис** (для Telegram бота)

#### Вариант A: Через веб-интерфейс (рекомендуется)

1. **Создайте первый сервис (API):**
   - В Railway проекте: **New** → **GitHub Repo**
   - Выберите репозиторий: `beauty-school`
   - Название: `beauty-school-api`
   - **Settings** → **Start Command:** `python run_api.py`
   - Добавьте переменные окружения (см. выше)

2. **Создайте второй сервис (Bot):**
   - В том же проекте Railway: **New** → **GitHub Repo**
   - Выберите тот же репозиторий: `beauty-school`
   - Название: `beauty-school-bot`
   - **Settings** → **Start Command:** `python run_bot_production.py`
   - Добавьте те же переменные окружения

3. **Подключите оба сервиса к одной БД:**
   - В каждом сервисе: **Settings** → **Variables**
   - **Add Reference** → выберите PostgreSQL → `DATABASE_URL`

#### Вариант B: Через CLI

```bash
# Создайте проект
railway init

# Создайте API сервис
railway service create beauty-school-api
railway service use beauty-school-api
railway variables set START_COMMAND="python run_api.py"

# Создайте Bot сервис
railway service create beauty-school-bot
railway service use beauty-school-bot
railway variables set START_COMMAND="python run_bot_production.py"
```

### 7. Деплой

```bash
railway up
```

Railway автоматически:
- Определит Python проект
- Установит зависимости из `requirements.txt`
- Запустит соответствующий скрипт для каждого сервиса

### 7. Получите URL

```bash
railway domain
```

Или в веб-интерфейсе Railway → Settings → Domains

---

## Через веб-интерфейс (проще)

### 1. Зайдите на [railway.app](https://railway.app)

### 2. New Project → Deploy from GitHub repo

### 3. Выберите ваш репозиторий `beauty-school`

### 4. Настройки:

- **Root Directory:** оставьте пустым (корень проекта)
- **Build Command:** (Railway определит автоматически)
- **Start Command:** `python run_api.py`

### 5. Добавьте PostgreSQL:

- New → Database → PostgreSQL
- Railway создаст переменную `DATABASE_URL` автоматически

### 6. Добавьте переменные окружения:

Settings → Variables → Add Variable:

```
BOT_TOKEN=your_bot_token
ADMIN_BOT_TOKEN=your_admin_bot_token
ADMIN_IDS=your_telegram_id
ENVIRONMENT=production
FRONTEND_URL=https://beauty-school-two.vercel.app
WEBAPP_URL=https://beauty-school-two.vercel.app
SECRET_KEY=your_secret_key_here
```

**Важно:** Railway автоматически использует `DATABASE_URL` из PostgreSQL сервиса.

### 7. Деплой

Railway автоматически задеплоит при push в GitHub!

---

## После деплоя

### 1. Получите URL вашего backend

Railway даст URL типа: `https://beauty-school-backend.railway.app`

### 2. Обновите Vercel

В Vercel → Settings → Environment Variables:
- `VITE_API_URL` = `https://beauty-school-backend.railway.app/api`

### 3. Обновите .env локально

```bash
BACKEND_URL=https://beauty-school-backend.railway.app/api
```

### 4. Перезапустите бота

Перезапустите бота, чтобы он использовал новый `WEBAPP_URL`.

---

## Миграции базы данных

После создания PostgreSQL базы:

```bash
# Подключитесь к Railway
railway link

# Запустите миграции
railway run alembic upgrade head
```

Или через веб-интерфейс Railway → Database → Connect → выполните SQL.

---

## Проверка

После деплоя проверьте:

1. ✅ Health endpoint: `https://your-backend.railway.app/health`
2. ✅ API docs: `https://your-backend.railway.app/api/docs`
3. ✅ Frontend может делать запросы к API

---

## Troubleshooting

### Ошибка: "Module not found"

**Решение:** Проверьте что все зависимости в `requirements.txt`.

### Ошибка: "Database connection failed"

**Решение:** 
1. Проверьте что PostgreSQL сервис запущен
2. Проверьте что `DATABASE_URL` установлен (Railway должен добавить автоматически)

### Ошибка: "Port already in use"

**Решение:** Railway автоматически определяет порт через переменную `PORT`. Не нужно указывать порт вручную.

### Backend не отвечает

**Решение:**
1. Проверьте логи: Railway → Deployments → View Logs
2. Проверьте что `python run_api.py` запускается
3. Проверьте переменные окружения

---

## Автоматический деплой

Railway автоматически деплоит при каждом push в `main` ветку GitHub!

---

## Стоимость

Railway дает бесплатный план:
- $5 кредитов в месяц
- Достаточно для небольшого проекта
- PostgreSQL бесплатно (до 512MB)

---

## Готово! 🎉

После деплоя ваш backend будет доступен по HTTPS и Mini App сможет работать полноценно!

