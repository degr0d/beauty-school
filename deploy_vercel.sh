#!/bin/bash
# Скрипт для деплоя на Vercel

echo "🚀 Деплой на Vercel"
echo ""

# Проверяем что мы в правильной директории
if [ ! -f "package.json" ]; then
    echo "❌ Запустите скрипт из папки frontend"
    exit 1
fi

# Проверяем что Vercel CLI установлен
if ! command -v vercel &> /dev/null; then
    echo "📦 Установка Vercel CLI..."
    npm i -g vercel
fi

# Проверяем сборку
echo "🔨 Проверка сборки..."
if npm run build; then
    echo "✅ Сборка успешна!"
else
    echo "❌ Ошибка сборки"
    exit 1
fi

# Деплой
echo ""
echo "🚀 Запуск деплоя..."
vercel

echo ""
echo "✅ После деплоя:"
echo "1. Скопируйте URL из Vercel (например: https://beauty-school.vercel.app)"
echo "2. Обновите .env: WEBAPP_URL=https://your-url.vercel.app"
echo "3. В настройках Vercel проекта добавьте переменную:"
echo "   VITE_API_URL=https://your-backend-url.com/api"

