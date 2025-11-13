"""
Сервис для генерации PDF сертификатов
"""

import os
from datetime import datetime
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

from backend.database.models import User, Course


def generate_certificate_number(user_id: int, course_id: int) -> str:
    """
    Генерирует уникальный номер сертификата
    Формат: CERT-{user_id}-{course_id}-{timestamp}
    """
    timestamp = datetime.now().strftime("%Y%m%d")
    return f"CERT-{user_id:05d}-{course_id:03d}-{timestamp}"


def generate_certificate_pdf(
    user: User,
    course: Course,
    output_path: str,
    certificate_number: str
) -> str:
    """
    Генерирует PDF сертификат о прохождении курса
    
    Args:
        user: Пользователь
        course: Курс
        output_path: Путь для сохранения PDF
        certificate_number: Номер сертификата
    
    Returns:
        Путь к созданному PDF файлу
    """
    # Создаем директорию если её нет
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Создаем PDF документ
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=30*mm,
        leftMargin=30*mm,
        topMargin=30*mm,
        bottomMargin=30*mm
    )
    
    # Стили
    styles = getSampleStyleSheet()
    
    # Заголовок сертификата
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor('#E91E63'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Имя пользователя
    name_style = ParagraphStyle(
        'CustomName',
        parent=styles['Heading2'],
        fontSize=28,
        textColor=colors.HexColor('#333333'),
        spaceAfter=15,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Текст сертификата
    text_style = ParagraphStyle(
        'CustomText',
        parent=styles['Normal'],
        fontSize=16,
        textColor=colors.HexColor('#666666'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    # Номер сертификата
    number_style = ParagraphStyle(
        'CustomNumber',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#999999'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Oblique'
    )
    
    # Строим содержимое PDF
    story = []
    
    # Заголовок
    story.append(Paragraph("СЕРТИФИКАТ", title_style))
    story.append(Spacer(1, 20*mm))
    
    # Текст о выдаче
    story.append(Paragraph(
        "Настоящим подтверждается, что",
        text_style
    ))
    story.append(Spacer(1, 10*mm))
    
    # Имя пользователя
    story.append(Paragraph(
        f"<b>{user.full_name}</b>",
        name_style
    ))
    story.append(Spacer(1, 10*mm))
    
    # Описание курса
    story.append(Paragraph(
        "успешно завершил(а) курс",
        text_style
    ))
    story.append(Spacer(1, 5*mm))
    
    story.append(Paragraph(
        f"<b>«{course.title}»</b>",
        name_style
    ))
    story.append(Spacer(1, 15*mm))
    
    # Дата выдачи
    issue_date = datetime.now().strftime("%d.%m.%Y")
    story.append(Paragraph(
        f"Дата выдачи: {issue_date}",
        text_style
    ))
    story.append(Spacer(1, 20*mm))
    
    # Номер сертификата
    story.append(Paragraph(
        f"Номер сертификата: {certificate_number}",
        number_style
    ))
    
    # Создаем PDF
    doc.build(story)
    
    return output_path


def save_certificate_to_storage(
    user: User,
    course: Course,
    certificate_number: str,
    storage_path: Optional[str] = None
) -> str:
    """
    Сохраняет сертификат в хранилище и возвращает путь/URL
    
    Args:
        user: Пользователь
        course: Курс
        certificate_number: Номер сертификата
        storage_path: Путь для хранения (если None - используется локальная папка certificates)
    
    Returns:
        Путь к файлу сертификата
    """
    if storage_path is None:
        # Используем локальное хранилище
        storage_path = "certificates"
    
    # Создаем директорию если её нет
    os.makedirs(storage_path, exist_ok=True)
    
    # Имя файла
    filename = f"{certificate_number}.pdf"
    filepath = os.path.join(storage_path, filename)
    
    # Генерируем PDF
    generate_certificate_pdf(user, course, filepath, certificate_number)
    
    return filepath


def get_certificate_url(filepath: str, base_url: Optional[str] = None) -> str:
    """
    Возвращает URL для доступа к сертификату
    
    Args:
        filepath: Путь к файлу
        base_url: Базовый URL (если None - возвращается относительный путь)
    
    Returns:
        URL сертификата
    """
    if base_url:
        # Если есть базовый URL - формируем полный URL
        filename = os.path.basename(filepath)
        return f"{base_url}/certificates/{filename}"
    else:
        # Возвращаем относительный путь
        return f"/certificates/{os.path.basename(filepath)}"

