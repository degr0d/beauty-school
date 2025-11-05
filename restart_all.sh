#!/bin/bash

# ============================================
# Полный перезапуск всего проекта (Mac)
# Останавливает всё и запускает заново
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "============================================"
echo "  🔄 ПОЛНЫЙ ПЕРЕЗАПУСК ПРОЕКТА"
echo "============================================"
echo ""

# Шаг 1: Остановка всех процессов
echo "[1/4] Остановка всех процессов..."
echo ""

# Останавливаем Python процессы (бот и API)
pkill -f "python.*run_all.py" 2>/dev/null && echo -e "${GREEN}✓${NC} Backend остановлен" || echo "Backend не был запущен"
pkill -f "python.*run_bot_full.py" 2>/dev/null && echo -e "${GREEN}✓${NC} Bot остановлен" || true
pkill -f "python.*run_api.py" 2>/dev/null && echo -e "${GREEN}✓${NC} API остановлен" || true

# Останавливаем Frontend (Vite)
pkill -f "node.*vite" 2>/dev/null && echo -e "${GREEN}✓${NC} Frontend остановлен" || echo "Frontend не был запущен"

# Останавливаем по PID файлам (если есть)
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid 2>/dev/null)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    rm -f .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid 2>/dev/null)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    rm -f .frontend.pid
fi

sleep 2
echo ""

# Шаг 2: Проверка Docker
echo "[2/4] Проверка Docker контейнеров..."
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker не запущен!${NC}"
    echo "Запустите Docker Desktop и повторите попытку."
    exit 1
fi

# Перезапускаем Docker контейнеры
if ! docker-compose ps | grep -q "Up"; then
    docker-compose up -d
    echo "Ожидание готовности базы данных..."
    sleep 5
fi
echo -e "${GREEN}✓${NC} Docker контейнеры готовы"
echo ""

# Шаг 3: Подготовка окружения
echo "[3/4] Подготовка окружения..."

# Активация venv
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "Создание виртуального окружения..."
    python3 -m venv venv
fi

source venv/bin/activate

# Проверка зависимостей
if ! python -c "import aiogram" 2>/dev/null; then
    echo "Установка зависимостей..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi
echo -e "${GREEN}✓${NC} Окружение готово"
echo ""

# Шаг 4: Запуск всего
echo "[4/4] Запуск всех сервисов..."
echo ""

# Запуск Backend (Bot + API)
echo "🚀 Запуск Backend (Bot + API)..."
cd "$(dirname "$0")"
python run_all.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > .backend.pid
sleep 5
echo -e "${GREEN}✓${NC} Backend запущен (PID: $BACKEND_PID)"
echo ""

# Запуск Frontend
echo "🚀 Запуск Frontend..."
cd frontend

# Проверка Node.js
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠ Node.js не установлен${NC}"
    echo "Frontend не будет запущен"
else
    # Проверка node_modules
    if [ ! -d "node_modules" ]; then
        echo "Установка npm зависимостей..."
        npm install
    fi
    
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    echo $FRONTEND_PID > .frontend.pid
    sleep 3
    echo -e "${GREEN}✓${NC} Frontend запущен (PID: $FRONTEND_PID)"
fi

cd ..
echo ""

echo "============================================"
echo -e "${GREEN}  ✅ ВСЕ СЕРВИСЫ ЗАПУЩЕНЫ!${NC}"
echo "============================================"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/api/docs"
echo ""
echo "Логи:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "Для остановки: ./stop.sh"
echo ""

