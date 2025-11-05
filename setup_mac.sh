#!/bin/bash

# ============================================
# Beauty School - Настройка для macOS
# ============================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "============================================"
echo "  Beauty School - Настройка для macOS"
echo "============================================"
echo ""

# 1. Проверка Python
echo "[1/6] Проверка Python..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 не установлен!${NC}"
    echo "Установите Python 3 через Homebrew:"
    echo "  brew install python3"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
echo ""

# 2. Создание .env файла
echo "[2/6] Проверка .env файла..."
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠ Файл .env не найден${NC}"
    if [ -f config.example ]; then
        cp config.example .env
        echo -e "${GREEN}✓${NC} Создан .env из config.example"
        echo -e "${YELLOW}⚠ ВАЖНО: Отредактируйте .env и заполните все параметры!${NC}"
    else
        echo -e "${RED}❌ config.example не найден!${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} .env файл существует"
fi
echo ""

# 3. Пересоздание виртуального окружения
echo "[3/6] Настройка виртуального окружения Python..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Обнаружено существующее venv${NC}"
    read -p "Пересоздать? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        echo "Удалено старое окружение"
    fi
fi

if [ ! -d "venv" ]; then
    echo "Создание нового виртуального окружения..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Виртуальное окружение создано"
fi

source venv/bin/activate
echo -e "${GREEN}✓${NC} Виртуальное окружение активировано"
echo ""

# 4. Установка Python зависимостей
echo "[4/6] Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}✓${NC} Python зависимости установлены"
echo ""

# 5. Проверка и установка Node.js
echo "[5/6] Проверка Node.js..."
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}⚠ Node.js не установлен${NC}"
    echo "Установка через Homebrew..."
    if command -v brew &> /dev/null; then
        brew install node
    else
        echo -e "${RED}❌ Homebrew не установлен!${NC}"
        echo "Установите Node.js вручную: https://nodejs.org/"
        exit 1
    fi
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓${NC} Node.js $NODE_VERSION"
echo ""

# 6. Установка npm зависимостей
echo "[6/6] Установка npm зависимостей..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
    echo -e "${GREEN}✓${NC} npm зависимости установлены"
else
    echo -e "${GREEN}✓${NC} node_modules уже существует"
fi
cd ..
echo ""

# 7. Проверка Docker
echo "[Дополнительно] Проверка Docker..."
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}⚠ Docker не установлен${NC}"
    echo "Установите Docker Desktop для Mac: https://www.docker.com/products/docker-desktop"
else
    if docker info > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Docker запущен"
    else
        echo -e "${YELLOW}⚠ Docker не запущен${NC}"
        echo "Запустите Docker Desktop"
    fi
fi
echo ""

# Делаем скрипты исполняемыми
chmod +x launch.sh stop.sh setup_mac.sh

echo "============================================"
echo -e "${GREEN}  НАСТРОЙКА ЗАВЕРШЕНА!${NC}"
echo "============================================"
echo ""
echo "Следующие шаги:"
echo ""
echo "1. Отредактируйте .env файл и заполните все параметры:"
echo "   - BOT_TOKEN (от @BotFather)"
echo "   - ADMIN_BOT_TOKEN"
echo "   - ADMIN_IDS (ваш Telegram ID)"
echo "   - DB_PASSWORD"
echo ""
echo "2. Запустите Docker контейнеры:"
echo "   docker-compose up -d"
echo ""
echo "3. Примените миграции базы данных:"
echo "   source venv/bin/activate"
echo "   alembic upgrade head"
echo ""
echo "4. (Опционально) Заполните тестовыми данными:"
echo "   python -m backend.database.seed_data"
echo ""
echo "5. Запустите проект:"
echo "   ./launch.sh"
echo ""
echo "Для остановки:"
echo "   ./stop.sh"
echo ""

