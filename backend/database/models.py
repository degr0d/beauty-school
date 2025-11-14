"""
SQLAlchemy модели базы данных
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DECIMAL,
    TIMESTAMP, ForeignKey, BigInteger, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.database.database import Base


# ========================================
# 1. Users - Пользователи
# ========================================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    city = Column(String(100), nullable=True)
    consent_personal_data = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    points = Column(Integer, default=0, nullable=False)  # Баллы геймификации
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user_courses = relationship("UserCourse", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")
    achievements = relationship("UserAchievement", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, name={self.full_name})>"


# ========================================
# 2. Courses - Курсы
# ========================================
class Course(Base):
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)  # Краткое описание
    full_description = Column(Text, nullable=True)  # Полное описание
    category = Column(String(100), nullable=False, index=True)  # manicure, eyelashes и т.д.
    cover_image_url = Column(Text, nullable=True)
    is_top = Column(Boolean, default=False, nullable=False)  # Топ курс месяца
    price = Column(DECIMAL(10, 2), default=0, nullable=False)  # Цена (для будущей оплаты)
    duration_hours = Column(Integer, nullable=True)  # Длительность в часах
    is_active = Column(Boolean, default=True, nullable=False)  # Курс виден пользователям
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    lessons = relationship("Lesson", back_populates="course", order_by="Lesson.order")
    user_courses = relationship("UserCourse", back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title}, category={self.category})>"


# ========================================
# 3. Lessons - Уроки
# ========================================
class Lesson(Base):
    __tablename__ = "lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    order = Column(Integer, nullable=False)  # Порядковый номер урока
    video_url = Column(Text, nullable=True)  # URL видео
    video_duration = Column(Integer, nullable=True)  # Длительность в секундах
    pdf_url = Column(Text, nullable=True)  # URL PDF/чек-листа
    is_free = Column(Boolean, default=False, nullable=False)  # Бесплатный урок (превью)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    course = relationship("Course", back_populates="lessons")
    progress = relationship("UserProgress", back_populates="lesson")
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, course_id={self.course_id}, order={self.order}, title={self.title})>"


# ========================================
# 4. UserCourses - Доступ пользователей к курсам
# ========================================
class UserCourse(Base):
    __tablename__ = "user_courses"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    purchased_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_courses")
    course = relationship("Course", back_populates="user_courses")
    
    def __repr__(self):
        return f"<UserCourse(user_id={self.user_id}, course_id={self.course_id})>"


# ========================================
# 5. UserProgress - Прогресс по урокам
# ========================================
class UserProgress(Base):
    __tablename__ = "user_progress"
    __table_args__ = (
        UniqueConstraint("user_id", "lesson_id", name="uq_user_lesson"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False)
    completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    watch_time = Column(Integer, default=0, nullable=False)  # Время просмотра (секунды)
    
    # Relationships
    user = relationship("User", back_populates="progress")
    lesson = relationship("Lesson", back_populates="progress")
    
    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, lesson_id={self.lesson_id}, completed={self.completed})>"


# ========================================
# 6. Achievements - Достижения (ачивки)
# ========================================
class Achievement(Base):
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(Text, nullable=True)
    points = Column(Integer, default=0, nullable=False)  # Баллы за получение
    condition_type = Column(String(50), nullable=False)  # courses_completed, category_courses и т.д.
    condition_value = Column(Integer, nullable=False)  # Значение условия (например, 3 курса)
    
    # Relationships
    user_achievements = relationship("UserAchievement", back_populates="achievement")
    
    def __repr__(self):
        return f"<Achievement(id={self.id}, title={self.title})>"


# ========================================
# 7. UserAchievements - Полученные ачивки
# ========================================
class UserAchievement(Base):
    __tablename__ = "user_achievements"
    __table_args__ = (
        UniqueConstraint("user_id", "achievement_id", name="uq_user_achievement"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    earned_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
    
    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"


# ========================================
# 8. Communities - Сообщества/чаты
# ========================================
class Community(Base):
    __tablename__ = "communities"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # city или profession
    city = Column(String(100), nullable=True)  # Город (если type=city)
    category = Column(String(100), nullable=True)  # Категория профессии (если type=profession)
    telegram_link = Column(Text, nullable=False)  # Ссылка на Telegram-чат
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Community(id={self.id}, title={self.title}, type={self.type})>"


# ========================================
# 9. Payments - Платежи (ЮKassa)
# ========================================
class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)  # Сумма платежа
    yookassa_payment_id = Column(String(255), nullable=True, unique=True, index=True)  # ID платежа в ЮKassa
    status = Column(String(50), default="pending", nullable=False)  # pending, succeeded, canceled
    payment_method = Column(String(50), nullable=True)  # bank_card, yoo_money, etc.
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    paid_at = Column(TIMESTAMP, nullable=True)
    
    # Relationships
    user = relationship("User", backref="payments")
    course = relationship("Course", backref="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, status={self.status})>"


# ========================================
# 10. Certificates - Сертификаты
# ========================================
class Certificate(Base):
    __tablename__ = "certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, index=True)
    certificate_number = Column(String(100), unique=True, nullable=False, index=True)  # Уникальный номер сертификата
    certificate_url = Column(Text, nullable=False)  # Путь к PDF файлу
    issued_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)  # Дата выдачи
    
    # Relationships
    user = relationship("User", backref="certificates")
    course = relationship("Course", backref="certificates")
    
    def __repr__(self):
        return f"<Certificate(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, number={self.certificate_number})>"


# ========================================
# 11. Favorites - Избранные курсы
# ========================================
class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_favorite"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="favorites")
    course = relationship("Course", backref="favorites")
    
    def __repr__(self):
        return f"<Favorite(user_id={self.user_id}, course_id={self.course_id})>"


# ========================================
# 12. Review - Отзывы на курсы
# ========================================
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)  # Текст отзыва
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="reviews")
    course = relationship("Course", backref="reviews")
    
    def __repr__(self):
        return f"<Review(id={self.id}, user_id={self.user_id}, course_id={self.course_id}, rating={self.rating})>"


# ========================================
# 13. Challenge - Челленджи
# ========================================
class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon_url = Column(Text, nullable=True)
    points_reward = Column(Integer, default=0, nullable=False)  # Баллы за выполнение
    condition_type = Column(String(50), nullable=False)  # complete_lessons, complete_courses, earn_points и т.д.
    condition_value = Column(Integer, nullable=False)  # Значение условия
    start_date = Column(TIMESTAMP, nullable=True)  # Дата начала челленджа
    end_date = Column(TIMESTAMP, nullable=True)  # Дата окончания челленджа
    is_active = Column(Boolean, default=True, nullable=False)
    
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    user_challenges = relationship("UserChallenge", back_populates="challenge")
    
    def __repr__(self):
        return f"<Challenge(id={self.id}, title={self.title})>"


# ========================================
# 14. UserChallenge - Участие пользователей в челленджах
# ========================================
class UserChallenge(Base):
    __tablename__ = "user_challenges"
    __table_args__ = (
        UniqueConstraint("user_id", "challenge_id", name="uq_user_challenge"),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0, nullable=False)  # Текущий прогресс (например, 3 из 5 уроков)
    is_completed = Column(Boolean, default=False, nullable=False)
    completed_at = Column(TIMESTAMP, nullable=True)
    joined_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", backref="user_challenges")
    challenge = relationship("Challenge", back_populates="user_challenges")
    
    def __repr__(self):
        return f"<UserChallenge(user_id={self.user_id}, challenge_id={self.challenge_id}, progress={self.progress})>"


# ========================================
# 15. SupportTicket - Тикеты поддержки
# ========================================
class SupportTicket(Base):
    __tablename__ = "support_tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=True)  # Тема (опционально)
    status = Column(String(50), default="open", nullable=False)  # open, closed, pending
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="support_tickets")
    messages = relationship("SupportMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="SupportMessage.created_at")
    
    def __repr__(self):
        return f"<SupportTicket(id={self.id}, user_id={self.user_id}, status={self.status})>"


# ========================================
# 16. SupportMessage - Сообщения в тикетах поддержки
# ========================================
class SupportMessage(Base):
    __tablename__ = "support_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    is_from_admin = Column(Boolean, default=False, nullable=False)  # True если сообщение от админа
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    read_at = Column(TIMESTAMP, nullable=True)  # Когда админ прочитал сообщение
    
    # Relationships
    ticket = relationship("SupportTicket", back_populates="messages")
    user = relationship("User", backref="support_messages")
    
    def __repr__(self):
        return f"<SupportMessage(id={self.id}, ticket_id={self.ticket_id}, is_from_admin={self.is_from_admin})>"


# ========================================
# Пример использования в коде:
# ========================================
# from backend.database import async_session
# from backend.database.models import User, Course
# 
# async def get_user_courses(user_id: int):
#     async with async_session() as session:
#         result = await session.execute(
#             select(Course).join(UserCourse).where(UserCourse.user_id == user_id)
#         )
#         courses = result.scalars().all()
#         return courses

