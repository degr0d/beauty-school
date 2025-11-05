#!/bin/bash

# ============================================
# Beauty School - Stop Script для macOS
# ============================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "============================================"
echo "  Beauty School - Stopping..."
echo "============================================"
echo ""

# Остановка по PID файлам
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo "Остановка Backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
        rm .backend.pid
        echo -e "${GREEN}✓${NC} Backend остановлен"
    fi
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo "Остановка Frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        rm .frontend.pid
        echo -e "${GREEN}✓${NC} Frontend остановлен"
    fi
fi

# Дополнительная очистка процессов
echo "Очистка процессов..."
pkill -f "python.*run_all.py" 2>/dev/null || true
pkill -f "node.*vite" 2>/dev/null || true

echo ""
echo "============================================"
echo -e "${GREEN}  ВСЕ СЕРВИСЫ ОСТАНОВЛЕНЫ${NC}"
echo "============================================"
echo ""

