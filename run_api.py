"""
Запуск только FastAPI сервера
Для разработки и тестирования API
"""

import uvicorn
from backend.webapp.app import create_app

if __name__ == "__main__":
    """
    Запуск FastAPI сервера на порту 8000
    Swagger UI: http://localhost:8000/api/docs
    ReDoc: http://localhost:8000/api/redoc
    Health: http://localhost:8000/health
    """
    
    app = create_app()
    
    print("=" * 60)
    print("Beauty School API Server")
    print("=" * 60)
    print()
    print("Swagger UI:  http://localhost:8000/api/docs")
    print("ReDoc:       http://localhost:8000/api/redoc")
    print("Health:      http://localhost:8000/health")
    print()
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )

