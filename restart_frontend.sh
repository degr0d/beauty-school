#!/bin/bash
# Перезапуск Frontend после получения URL туннеля

echo "🔄 Перезапуск Frontend..."

# Останавливаем Frontend
pkill -f 'node.*vite' 2>/dev/null || true
pkill -f 'npm.*dev' 2>/dev/null || true
pkill -f 'vite' 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

sleep 2

# Проверяем что порт освобождён
if lsof -ti:5173 > /dev/null 2>&1; then
    echo "⚠️ Порт 5173 всё ещё занят, жду ещё..."
    sleep 3
fi

echo "✅ Frontend остановлен"
echo ""
echo "💡 Frontend перезапустится автоматически через launch.json"
echo "   (или перезапустите вручную через F5)"

