"""
API эндпоинты для сертификатов
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from backend.database import get_session, User, Course, Certificate
from backend.webapp.middleware import get_telegram_user
from backend.webapp.schemas import CertificateResponse
from backend.services.certificates import (
    generate_certificate_number,
    save_certificate_to_storage,
    get_certificate_url
)
from backend.config import settings
import os

router = APIRouter()


@router.get("", response_model=List[CertificateResponse])
@router.get("/", response_model=List[CertificateResponse])
async def get_certificates(
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить список сертификатов пользователя
    """
    # Гарантируем, что telegram_id - это int
    telegram_id_raw = user["id"]
    telegram_id = int(telegram_id_raw) if telegram_id_raw else None
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Invalid telegram_id in user data")
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем сертификаты пользователя
    result = await session.execute(
        select(Certificate, Course)
        .join(Course, Certificate.course_id == Course.id)
        .where(Certificate.user_id == db_user.id)
        .order_by(Certificate.issued_at.desc())
    )
    certificates_data = result.all()
    
    certificates = []
    for cert, course in certificates_data:
        certificates.append(CertificateResponse(
            id=cert.id,
            course_id=cert.course_id,
            course_title=course.title,
            certificate_url=cert.certificate_url,
            certificate_number=cert.certificate_number,
            issued_at=cert.issued_at.isoformat() if hasattr(cert.issued_at, 'isoformat') else str(cert.issued_at)
        ))
    
    return certificates


@router.get("/course/{course_id}", response_model=CertificateResponse)
async def get_certificate_by_course(
    course_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Получить сертификат по конкретному курсу
    """
    # Гарантируем, что telegram_id - это int
    telegram_id_raw = user["id"]
    telegram_id = int(telegram_id_raw) if telegram_id_raw else None
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Invalid telegram_id in user data")
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем сертификат
    result = await session.execute(
        select(Certificate, Course)
        .join(Course, Certificate.course_id == Course.id)
        .where(
            Certificate.user_id == db_user.id,
            Certificate.course_id == course_id
        )
    )
    cert_data = result.first()
    
    if not cert_data:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    cert, course = cert_data
    
    return CertificateResponse(
        id=cert.id,
        course_id=cert.course_id,
        course_title=course.title,
        certificate_url=cert.certificate_url,
        certificate_number=cert.certificate_number,
        issued_at=cert.issued_at.isoformat() if hasattr(cert.issued_at, 'isoformat') else str(cert.issued_at)
    )


@router.get("/{certificate_id}/download")
async def download_certificate(
    certificate_id: int,
    user: dict = Depends(get_telegram_user),
    session: AsyncSession = Depends(get_session)
):
    """
    Скачать PDF сертификат
    """
    # Гарантируем, что telegram_id - это int
    telegram_id_raw = user["id"]
    telegram_id = int(telegram_id_raw) if telegram_id_raw else None
    
    if not telegram_id:
        raise HTTPException(status_code=400, detail="Invalid telegram_id in user data")
    
    # Получаем пользователя
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    db_user = result.scalar_one_or_none()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Получаем сертификат
    result = await session.execute(
        select(Certificate).where(
            Certificate.id == certificate_id,
            Certificate.user_id == db_user.id
        )
    )
    cert = result.scalar_one_or_none()
    
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    
    # Проверяем наличие файла
    if not cert.certificate_url:
        raise HTTPException(status_code=404, detail="Certificate file not found")
    
    # Путь к файлу (может быть относительным или абсолютным)
    filepath = cert.certificate_url
    if not os.path.isabs(filepath):
        # Если относительный путь - добавляем базовый путь
        storage_path = getattr(settings, 'LOCAL_STORAGE_PATH', './certificates')
        filepath = os.path.join(storage_path, os.path.basename(filepath))
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Certificate file not found on server")
    
    return FileResponse(
        filepath,
        media_type="application/pdf",
        filename=f"certificate_{cert.certificate_number}.pdf"
    )

