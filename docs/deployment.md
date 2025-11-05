# 🚀 Гайд по развёртыванию (Deployment)

## Варианты хостинга

### 1. VPS (рекомендуется для MVP)

**Преимущества:**
- Полный контроль
- Низкая стоимость (~500-1000₽/мес)
- Подходит для старта

**Провайдеры:**
- Timeweb (Россия)
- Selectel (Россия)
- DigitalOcean (международный)
- VK Cloud (Россия)

**Минимальные требования:**
- 2GB RAM
- 1 CPU
- 20GB SSD
- Ubuntu 20.04 или выше

---

## Развёртывание на VPS (пошаговая инструкция)

### Шаг 1: Подготовка сервера

```bash
# Подключаемся по SSH
ssh root@your_server_ip

# Обновляем систему
apt update && apt upgrade -y

# Устанавливаем необходимые пакеты
apt install -y git curl wget python3-pip python3-venv nginx certbot python3-certbot-nginx

# Устанавливаем Docker и Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install -y docker-compose
```

### Шаг 2: Клонирование репозитория

```bash
# Создаём директорию для проекта
mkdir -p /var/www/beauty-school
cd /var/www/beauty-school

# Клонируем репозиторий (замените на ваш URL)
git clone https://github.com/yourusername/beauty-school.git .
```

### Шаг 3: Настройка переменных окружения

```bash
# Копируем пример конфигурации
cp config.example .env

# Редактируем .env файл
nano .env
```

**Заполните следующие параметры:**

```env
# Telegram Bot Tokens (получить у @BotFather)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_BOT_TOKEN=987654321:ZYXwvuTSRqpONMlkJIhGFedCBA

# Admin IDs (ваши Telegram User ID)
ADMIN_IDS=123456789,987654321

# Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=beauty_db
DB_USER=beauty_user
DB_PASSWORD=СИЛЬНЫЙ_ПАРОЛЬ_ЗДЕСЬ

# API URLs (замените на ваш домен)
FRONTEND_URL=https://yourdomain.com
BACKEND_URL=https://yourdomain.com/api

# Secret Key (сгенерируйте случайную строку)
SECRET_KEY=$(openssl rand -hex 32)

# Environment
ENVIRONMENT=production

# Logging
LOG_LEVEL=INFO
```

### Шаг 4: Запуск Docker Compose

```bash
# Запускаем контейнеры
docker-compose -f docker-compose.yml up -d

# Проверяем статус
docker-compose ps
```

### Шаг 5: Применение миграций БД

```bash
# Входим в контейнер backend
docker-compose exec backend bash

# Применяем миграции
alembic upgrade head

# Выходим
exit
```

### Шаг 6: Настройка Nginx

```bash
# Создаём конфиг для Nginx
nano /etc/nginx/sites-available/beauty-school
```

**Содержимое файла:**

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    # Frontend (статика)
    location / {
        root /var/www/beauty-school/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Health check
    location /health {
        proxy_pass http://localhost:8000/health;
    }
}
```

```bash
# Создаём симлинк
ln -s /etc/nginx/sites-available/beauty-school /etc/nginx/sites-enabled/

# Удаляем дефолтный конфиг
rm /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
nginx -t

# Перезапускаем Nginx
systemctl restart nginx
```

### Шаг 7: SSL сертификат (Let's Encrypt)

```bash
# Получаем SSL сертификат
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Вводим email и соглашаемся с условиями

# Проверяем автообновление
certbot renew --dry-run
```

### Шаг 8: Сборка фронтенда

```bash
# Устанавливаем Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# Переходим в папку фронтенда
cd /var/www/beauty-school/frontend

# Устанавливаем зависимости
npm install

# Создаём .env для фронтенда
echo "VITE_API_URL=https://yourdomain.com/api" > .env

# Собираем продакшен-версию
npm run build

# Перезапускаем Nginx
systemctl restart nginx
```

---

## Настройка Telegram ботов

### 1. Создание ботов через @BotFather

```
1. Найдите @BotFather в Telegram
2. Отправьте команду: /newbot
3. Введите название: "Beauty School"
4. Введите username: "beauty_school_bot"
5. Скопируйте токен

Повторите для админ-бота:
6. /newbot
7. Название: "Beauty School Admin"
8. Username: "beauty_school_admin_bot"
9. Скопируйте токен
```

### 2. Настройка Webhook (опционально)

Для использования Webhook вместо polling:

```bash
# Установите webhook для основного бота
curl -F "url=https://yourdomain.com/webhook/bot" \
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook

# Для админ-бота
curl -F "url=https://yourdomain.com/webhook/admin" \
     https://api.telegram.org/bot<ADMIN_BOT_TOKEN>/setWebhook
```

### 3. Настройка Menu Button (для Mini App)

```bash
curl -X POST https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setChatMenuButton \
  -H "Content-Type: application/json" \
  -d '{
    "menu_button": {
      "type": "web_app",
      "text": "Открыть приложение",
      "web_app": {
        "url": "https://yourdomain.com"
      }
    }
  }'
```

---

## Мониторинг и логи

### Просмотр логов

```bash
# Логи всех контейнеров
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend

# Логи Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Настройка автозапуска

```bash
# Docker Compose автоматически перезапускает контейнеры
# Проверяем политику restart в docker-compose.yml:
# restart: unless-stopped

# Включаем автозапуск Docker при загрузке системы
systemctl enable docker
```

---

## Обновление приложения

```bash
# Переходим в папку проекта
cd /var/www/beauty-school

# Подтягиваем изменения из Git
git pull origin main

# Пересобираем backend
docker-compose build backend
docker-compose up -d backend

# Применяем миграции (если есть)
docker-compose exec backend alembic upgrade head

# Пересобираем frontend
cd frontend
npm install
npm run build

# Перезапускаем Nginx
systemctl restart nginx
```

---

## Бэкапы

### Автоматический бэкап БД

Создайте скрипт `/root/backup-db.sh`:

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/backups/beauty-school"
mkdir -p $BACKUP_DIR

# Дамп БД
docker-compose exec -T postgres pg_dump -U beauty_user beauty_db > $BACKUP_DIR/backup_$DATE.sql

# Сжатие
gzip $BACKUP_DIR/backup_$DATE.sql

# Удаляем старые бэкапы (старше 30 дней)
find $BACKUP_DIR -type f -mtime +30 -delete

echo "Бэкап создан: backup_$DATE.sql.gz"
```

```bash
# Делаем исполняемым
chmod +x /root/backup-db.sh

# Добавляем в cron (каждый день в 3:00)
crontab -e
# Добавляем строку:
0 3 * * * /root/backup-db.sh >> /var/log/backup.log 2>&1
```

---

## Troubleshooting

### Проблема: Бот не отвечает

```bash
# Проверяем логи бота
docker-compose logs backend | grep -i error

# Проверяем, запущен ли контейнер
docker-compose ps

# Перезапускаем
docker-compose restart backend
```

### Проблема: Frontend не отображается

```bash
# Проверяем, собран ли фронтенд
ls -la /var/www/beauty-school/frontend/dist

# Проверяем Nginx
nginx -t
systemctl status nginx

# Проверяем права доступа
chmod -R 755 /var/www/beauty-school/frontend/dist
```

### Проблема: БД недоступна

```bash
# Проверяем статус контейнера PostgreSQL
docker-compose ps postgres

# Проверяем логи
docker-compose logs postgres

# Перезапускаем
docker-compose restart postgres
```

---

## Безопасность

### 1. Firewall

```bash
# Включаем UFW
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### 2. Обновления

```bash
# Настроить автоматические обновления
apt install unattended-upgrades
dpkg-reconfigure --priority=low unattended-upgrades
```

### 3. Fail2Ban (защита от брутфорса)

```bash
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

---

## Готово! 🎉

Ваше приложение доступно по адресу: `https://yourdomain.com`

Проверьте:
- [ ] Frontend открывается
- [ ] Бот отвечает на `/start`
- [ ] Админ-бот работает
- [ ] SSL сертификат установлен
- [ ] Логи пишутся корректно

