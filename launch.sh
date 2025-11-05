#!/bin/bash

# ============================================
# Beauty School - Launcher для macOS
# ============================================

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "============================================"
echo "  Beauty School - Starting..."
echo "============================================"
echo ""

# Проверка .env файла
if [ ! -f .env ]; then
    echo -e "${RED}❌ Файл .env не найден!${NC}"
    echo "Создайте его из config.example:"
    echo "  cp config.example .env"
    echo "Затем заполните все необходимые параметры."
    exit 1
fi

# Остановка старых процессов
echo "[1/4] Остановка старых процессов..."
pkill -f "python.*run_all.py" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓${NC} Готово!"
echo ""

# Проверка Docker
echo "[2/4] Проверка Docker..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker не запущен!${NC}"
    echo "Запустите Docker Desktop и повторите попытку."
    exit 1
fi

# Запуск Docker контейнеров (PostgreSQL, Redis)
echo "[3/4] Запуск Docker контейнеров..."
if ! docker-compose ps | grep -q "Up"; then
    docker-compose up -d
    echo "Ожидание готовности базы данных..."
    sleep 5
fi
echo -e "${GREEN}✓${NC} Docker контейнеры запущены!"
echo ""

# Активация виртуального окружения
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo -e "${YELLOW}⚠ Виртуальное окружение не найдено!${NC}"
    echo "Создание нового виртуального окружения..."
    python3 -m venv venv
fi

source venv/bin/activate

# Проверка установленных зависимостей
if ! python -c "import aiogram" 2>/dev/null; then
    echo "Установка Python зависимостей..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# Запуск Backend (Bot + API)
echo "[4/4] Запуск Backend (Bot + API)..."
python run_all.py &
BACKEND_PID=$!
sleep 5
echo -e "${GREEN}✓${NC} Backend запущен (PID: $BACKEND_PID)!"
echo ""

# Запуск Frontend
echo "Запуск Frontend..."
cd frontend

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js не установлен!${NC}"
    echo "Установите Node.js: https://nodejs.org/"
    echo "Или через Homebrew: brew install node"
    exit 1
fi

# Проверка node_modules
if [ ! -d "node_modules" ]; then
    echo "Установка npm зависимостей..."
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ..
sleep 3
echo -e "${GREEN}✓${NC} Frontend запущен (PID: $FRONTEND_PID)!"
echo ""

echo "============================================"
echo -e "${GREEN}  ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!${NC}"
echo "============================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/api/docs"
echo ""
echo "PID процессов сохранены в .pids файл для остановки"
echo "$BACKEND_PID" > .backend.pid
echo "$FRONTEND_PID" > .frontend.pid
echo ""
echo "Для остановки выполните: ./stop.sh"
echo ""
echo "Открытие браузера через 3 секунды..."
sleep 3
open http://localhost:5173

