# 🎯 НАЧНИТЕ ЗДЕСЬ!

## 👋 Добро пожаловать в Beauty School Project!

Вы получили **полностью готовый прототип** Telegram Mini App для бьюти-школы с подробными комментариями и документацией.

---

## 🗺️ Быстрая навигация

### 📖 Для начала работы
👉 **[docs/quickstart.md](docs/quickstart.md)** - Запустите проект за 10 минут
👉 **[docs/testing-guide.md](docs/testing-guide.md)** - Как тестировать

### 📚 Документация
- **[README.md](README.md)** - Обзор проекта и структуры

### 🏗️ Архитектура
- **[docs/architecture.md](docs/architecture.md)** - Как всё устроено
- **[docs/database.md](docs/database.md)** - Схема базы данных
- **[docs/mvp-roadmap.md](docs/mvp-roadmap.md)** - План разработки

### 🚀 Деплой
- **[docs/deployment.md](docs/deployment.md)** - Гайд по развёртыванию

---

## ⚡ Быстрый старт (3 команды)

```bash
# 1. Запустите базу данных
docker-compose up -d

# 2. Установите зависимости и запустите backend
pip install -r requirements.txt
python backend/main.py

# 3. Запустите frontend (в новом терминале)
cd frontend && npm install && npm run dev
```

**Готово!** Откройте http://localhost:5173

Подробнее → [docs/quickstart.md](docs/quickstart.md)

---

## 📂 Структура проекта

```
beauty/
├── 📄 START_HERE.md          ← ВЫ ЗДЕСЬ
├── 📄 README.md               ← Полное описание
│
├── 📁 docs/                   ← Документация
│   ├── quickstart.md          ← Быстрый старт
│   ├── testing-guide.md       ← Гайд по тестированию
│   ├── architecture.md        ← Архитектура
│   ├── database.md            ← Схема БД
│   ├── mvp-roadmap.md         ← План MVP
│   └── deployment.md          ← Деплой гайд
│
├── 📁 backend/                ← Python Backend
│   ├── bot/                   ← Telegram бот (регистрация)
│   ├── admin_bot/             ← Админ-бот (аналитика)
│   ├── webapp/                ← FastAPI (REST API)
│   ├── database/              ← SQLAlchemy модели
│   ├── services/              ← Бизнес-логика
│   └── utils/                 ← Утилиты
│
├── 📁 frontend/               ← React + TypeScript
│   └── src/
│       ├── pages/             ← Страницы Mini App
│       ├── components/        ← React компоненты
│       ├── api/               ← API клиент
│       └── hooks/             ← React hooks
│
├── 🚀 START_ALL.cmd           ← Запуск всего (Бот+API+Frontend)
├── 🐳 docker-compose.yml      ← PostgreSQL + Redis
└── ⚙️ config.example          ← Пример конфигурации
```

---

## ✅ Что готово

### Backend (Python)
- ✅ Telegram Bot (онбординг, регистрация через FSM)
- ✅ FastAPI REST API (курсы, уроки, профиль, прогресс)
- ✅ Admin Bot (статистика, управление)
- ✅ PostgreSQL + SQLAlchemy (8 моделей)
- ✅ Middleware для проверки Telegram initData

### Frontend (React)
- ✅ Telegram Mini App интеграция
- ✅ 6 страниц (главная, курсы, урок, профиль, сообщества)
- ✅ API клиент с автоматической авторизацией
- ✅ Роутинг, компоненты, стили

### DevOps
- ✅ Docker Compose для разработки
- ✅ Готовые конфиги для продакшена
- ✅ Alembic миграции

### Документация
- ✅ 4 подробных MD файла с примерами
- ✅ Комментарии во всех файлах
- ✅ Гайд по деплою на VPS

---

## 🎯 Что делать дальше?

### Шаг 1: Настройка (5 мин)
```bash
# Создайте .env файл
cp config.example .env

# Получите токены у @BotFather
# Заполните BOT_TOKEN, ADMIN_BOT_TOKEN, ADMIN_IDS
```

### Шаг 2: Запуск (5 мин)
Следуйте → [docs/quickstart.md](docs/quickstart.md)

### Шаг 3: Добавьте контент (10 мин)
```bash
# Добавьте свои курсы
# Отредактируйте: backend/database/seed_data.py
python -m backend.database.seed_data
```

### Шаг 4: Кастомизация (опционально)
- Измените дизайн: `frontend/src/styles/global.css`
- Добавьте обложки курсов
- Настройте категории

### Шаг 5: Деплой (1-2 часа)
Следуйте → [docs/deployment.md](docs/deployment.md)

---

## 🔥 Основные возможности

### Для учеников
- 📱 Регистрация через Telegram бота
- 📚 Каталог курсов с фильтрами
- 🎥 Просмотр видео-уроков
- 📄 Скачивание PDF материалов
- 📊 Прогресс-бар по курсам
- ✅ Отметка уроков как пройденных
- 👤 Личный профиль
- 💬 Сообщества по городам/направлениям

### Для админов
- 📈 Статистика пользователей
- 👥 Список учеников
- 📚 Управление курсами
- 🔍 Детальная аналитика

---

## 💡 Технологии

### Backend
- Python 3.11+
- aiogram 3.x (Telegram Bot)
- FastAPI (REST API)
- SQLAlchemy 2.0 (ORM)
- PostgreSQL (Database)
- Alembic (Migrations)

### Frontend
- React 18
- TypeScript
- Vite (Build tool)
- React Router (Navigation)
- Axios (HTTP client)
- Telegram Web App SDK

### DevOps
- Docker + Docker Compose
- Nginx (reverse proxy)
- Let's Encrypt (SSL)

---

## 📊 Прогресс MVP: 75% ✅

| Компонент | Готовность |
|-----------|-----------|
| 📚 Документация | 100% ✅ |
| 🗄️ База данных | 100% ✅ |
| 🤖 Telegram Bot | 90% ✅ |
| 🌐 REST API | 85% ✅ |
| ⚛️ Frontend UI | 60% ⚠️ |
| 👨‍💼 Админ-бот | 70% ⚠️ |

**Можно запускать!** Базовый MVP готов к тестированию.

---

## 🎓 Полезные команды

```bash
# Backend
python backend/main.py              # Запустить все сервисы
alembic upgrade head                # Применить миграции
python -m backend.database.seed_data # Заполнить тестовыми данными

# Frontend
cd frontend
npm install                         # Установить зависимости
npm run dev                         # Запустить dev-сервер
npm run build                       # Собрать для продакшена

# Docker
docker-compose up -d                # Запустить БД
docker-compose down                 # Остановить
docker-compose logs -f postgres     # Посмотреть логи
```

---

## ❓ Частые вопросы

**Q: Где взять токен бота?**  
A: @BotFather → `/newbot`

**Q: Как узнать свой Telegram ID?**  
A: @userinfobot

**Q: Нужен ли платный хостинг?**  
A: Для локальной разработки - нет. Для продакшена - VPS от 500₽/мес

**Q: Можно ли использовать без оплаты (ЮKassa)?**  
A: Да! Курсы можно делать бесплатными (price=0)

---

## 🆘 Нужна помощь?

1. ✅ Проверьте [docs/quickstart.md](docs/quickstart.md)
2. ✅ Посмотрите [docs/testing-guide.md](docs/testing-guide.md)
3. ✅ Проверьте логи: `python backend/main.py`
4. ✅ Проверьте Docker: `docker-compose ps`

---

## 🚀 Готовы начать?

### → **Windows**: Двойной клик на `START_ALL.cmd`
### → **Подробнее**: [docs/quickstart.md](docs/quickstart.md)

---

**Создано:** 27 октября 2025  
**Версия:** 0.1.0  
**Лицензия:** MIT

**Удачи в разработке! 💪**

