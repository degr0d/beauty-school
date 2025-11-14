"""
FastAPI приложение
Создание и настройка API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.webapp.routes import courses, lessons, profile, progress, communities, payment, access, achievements, leaderboard, favorites, reviews, notifications, challenges, certificates, analytics, support
from backend.webapp.middleware import TelegramAuthMiddleware
from backend.database.database import create_engine_and_session, get_engine, get_async_session
import asyncio
import logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Создаёт и настраивает FastAPI приложение
    """
    app = FastAPI(
        title="Beauty School API",
        description="API для Telegram Mini App бьюти-школы",
        version="0.1.0",
        docs_url="/api/docs" if settings.ENVIRONMENT == "development" else None,
        redoc_url="/api/redoc" if settings.ENVIRONMENT == "development" else None,
        redirect_slashes=False,  # Отключаем автоматический редирект со слэшем
    )
    
    # ========================================
    # CORS (для фронтенда)
    # ========================================
    # В режиме разработки разрешаем все origins (для работы через туннели)
    cors_origins = ["*"] if settings.ENVIRONMENT == "development" else [settings.FRONTEND_URL]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Добавляем middleware для логирования всех запросов
    # Временно отключено для диагностики проблемы с event loop
    # @app.middleware("http")
    # async def log_requests(request, call_next):
    #     print(f"📥 [Request] {request.method} {request.url.path}")
    #     print(f"   Origin: {request.headers.get('origin', 'N/A')}")
    #     print(f"   X-Telegram-Init-Data: {'Да' if request.headers.get('X-Telegram-Init-Data') else 'Нет'}")
    #     response = await call_next(request)
    #     print(f"📤 [Response] {request.method} {request.url.path} -> {response.status_code}")
    #     return response
    
    # ========================================
    # Middleware: Проверка Telegram initData
    # ========================================
    # Включаем middleware только в продакшене
    # В режиме разработки используем обход через X-Telegram-User-ID
    if settings.ENVIRONMENT == "production":
        app.add_middleware(TelegramAuthMiddleware)
        print("🔒 [App] TelegramAuthMiddleware включен (production mode)")
    else:
        print("🔧 [App] TelegramAuthMiddleware отключен (development mode - используем X-Telegram-User-ID)")
    
    # ========================================
    # Подключение роутеров
    # ========================================
    app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])
    app.include_router(lessons.router, prefix="/api/lessons", tags=["Lessons"])
    app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
    app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
    app.include_router(communities.router, prefix="/api/communities", tags=["Communities"])
    app.include_router(payment.router, prefix="/api/payment", tags=["Payment"])
    app.include_router(access.router, prefix="/api/access", tags=["Access"])
    app.include_router(achievements.router, prefix="/api/achievements", tags=["Achievements"])
    app.include_router(leaderboard.router, prefix="/api/leaderboard", tags=["Leaderboard"])
    app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
    app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
    app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
    app.include_router(challenges.router, prefix="/api/challenges", tags=["Challenges"])
    app.include_router(certificates.router, prefix="/api/certificates", tags=["Certificates"])
    app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
    app.include_router(support.router, prefix="/api/support", tags=["Support"])
    
    # Логирование зарегистрированных роутов для диагностики
    print("=" * 60)
    print("📋 Зарегистрированные роуты:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            print(f"   {list(route.methods)} {route.path}")
    print("=" * 60)
    
    # ========================================
    # Healthcheck эндпоинт
    # ========================================
    @app.get("/health")
    async def health():
        return {"status": "ok", "environment": settings.ENVIRONMENT}
    
    # ========================================
    # Startup/Shutdown events для правильной инициализации БД
    # ========================================
    @app.on_event("startup")
    async def startup_event():
        """
        Инициализация при запуске приложения
        Создаем engine и session в правильном event loop
        """
        logger.info("🚀 Application startup event")
        
        # КРИТИЧНО: создаем engine и session в startup_event
        # Это гарантирует правильный event loop
        try:
            create_engine_and_session()
            logger.info("✅ Database engine initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization warning: {e}")
        
        # Сохраняем в app.state для доступа из других мест (опционально)
        app.state.engine = get_engine()
        app.state.async_session = get_async_session()
        
        # Запускаем фоновую задачу для напоминаний
        asyncio.create_task(run_periodic_reminders())
        logger.info("✅ Background task for reminders started")
    
    async def run_periodic_reminders():
        """
        Фоновая задача: отправка напоминаний каждые 24 часа
        Автоматически запускается при старте API
        """
        from backend.services.scheduled_notifications import send_inactive_course_reminders
        from backend.database.database import get_async_session
        
        # Ждем 1 минуту после старта, чтобы БД точно была готова
        await asyncio.sleep(60)
        
        while True:
            try:
                logger.info("📱 Запуск отправки напоминаний о незавершенных курсах...")
                
                # Используем существующую фабрику сессий
                session_factory = get_async_session()
                async with session_factory() as session:
                    try:
                        result = await send_inactive_course_reminders(session)
                        logger.info(f"✅ Напоминания отправлены: {result}")
                    except Exception as e:
                        logger.error(f"❌ Ошибка отправки напоминаний: {e}")
                
                # Ждем 24 часа до следующего запуска
                await asyncio.sleep(24 * 60 * 60)  # 24 часа в секундах
                
            except asyncio.CancelledError:
                logger.info("⛔ Background task cancelled")
                break
            except Exception as e:
                logger.error(f"❌ Ошибка в фоновой задаче напоминаний: {e}")
                # При ошибке ждем 1 час перед повтором
                await asyncio.sleep(60 * 60)
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """
        Закрытие соединений при остановке приложения
        """
        if hasattr(app.state, 'engine') and app.state.engine:
            await app.state.engine.dispose()
        print("✅ Database connections closed")
    
    return app


# ========================================
# Для запуска через uvicorn напрямую:
# ========================================
# uvicorn backend.webapp.app:app --reload
app = create_app()

