"""
Обработка поддержки в админ-боте
"""

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, desc
from datetime import datetime

from backend.database import async_session, SupportTicket, SupportMessage, User
from backend.config import settings
from backend.admin_bot.filters import AdminFilter
from backend.services.notifications import send_notification

router = Router()

# Фильтр для админов - применяется ко всем обработчикам в этом роутере
router.message.filter(AdminFilter())


@router.message(Command("support"))
async def list_support_tickets(message: Message):
    """
    Список открытых тикетов поддержки
    """
    async with async_session() as session:
        # Получаем открытые тикеты
        result = await session.execute(
            select(SupportTicket, User)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.status == "open")
            .order_by(desc(SupportTicket.updated_at))
            .limit(10)
        )
        tickets = result.all()
    
    if not tickets:
        await message.answer("✅ Нет открытых тикетов поддержки")
        return
    
    tickets_list = []
    for ticket, user in tickets:
        # Подсчитываем непрочитанные сообщения
        result = await session.execute(
            select(SupportMessage)
            .where(
                SupportMessage.ticket_id == ticket.id,
                SupportMessage.is_from_admin == False,
                SupportMessage.read_at == None
            )
        )
        unread_count = len(result.scalars().all())
        
        unread_badge = f" 🔴 {unread_count}" if unread_count > 0 else ""
        
        tickets_list.append(
            f"• <b>#{ticket.id}</b> - {user.full_name}{unread_badge}\n"
            f"  📅 {ticket.updated_at.strftime('%d.%m.%Y %H:%M')}"
        )
    
    tickets_text = "\n\n".join(tickets_list)
    
    await message.answer(
        f"💬 <b>Открытые тикеты поддержки:</b>\n\n{tickets_text}\n\n"
        f"💡 Используйте /ticket <id> для просмотра и ответа",
        parse_mode="HTML"
    )


@router.message(Command("ticket"))
async def view_ticket(message: Message):
    """
    Просмотр тикета и ответ пользователю
    
    Формат: /ticket <ticket_id> [ответ]
    """
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer(
            "❌ Укажите ID тикета\n\n"
            "Формат: <code>/ticket 1</code> - просмотр тикета\n"
            "Или: <code>/ticket 1 Ваш ответ</code> - ответить пользователю",
            parse_mode="HTML"
        )
        return
    
    try:
        ticket_id = int(args[0])
    except ValueError:
        await message.answer("❌ Неверный формат ID тикета")
        return
    
    async with async_session() as session:
        # Получаем тикет
        result = await session.execute(
            select(SupportTicket, User)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.id == ticket_id)
        )
        ticket_data = result.first()
        
        if not ticket_data:
            await message.answer(f"❌ Тикет #{ticket_id} не найден")
            return
        
        ticket, user = ticket_data
        
        # Если есть текст ответа - отправляем ответ
        if len(args) > 1:
            reply_text = " ".join(args[1:])
            
            # Создаем сообщение от админа
            admin_message = SupportMessage(
                ticket_id=ticket.id,
                user_id=user.id,  # user_id должен быть ID пользователя из тикета
                message=reply_text,
                is_from_admin=True,
                read_at=datetime.now()
            )
            session.add(admin_message)
            
            # Отмечаем все сообщения пользователя как прочитанные
            result = await session.execute(
                select(SupportMessage)
                .where(
                    SupportMessage.ticket_id == ticket.id,
                    SupportMessage.is_from_admin == False,
                    SupportMessage.read_at == None
                )
            )
            unread_messages = result.scalars().all()
            for msg in unread_messages:
                msg.read_at = datetime.now()
            
            # Обновляем updated_at тикета
            ticket.updated_at = datetime.now()
            
            await session.commit()
            
            # Отправляем уведомление пользователю
            try:
                notification_text = (
                    f"💬 <b>Ответ от поддержки</b>\n\n"
                    f"📋 Тикет: #{ticket.id}\n\n"
                    f"{reply_text}"
                )
                await send_notification(user.telegram_id, notification_text)
            except Exception as e:
                print(f"⚠️ Ошибка отправки уведомления пользователю: {e}")
            
            await message.answer(
                f"✅ <b>Ответ отправлен!</b>\n\n"
                f"👤 Пользователю: {user.full_name}\n"
                f"📋 Тикет: #{ticket.id}\n\n"
                f"💬 Ваш ответ:\n{reply_text}",
                parse_mode="HTML"
            )
            return
        
        # Показываем тикет и сообщения
        result = await session.execute(
            select(SupportMessage)
            .where(SupportMessage.ticket_id == ticket.id)
            .order_by(SupportMessage.created_at)
        )
        messages = result.scalars().all()
        
        # Отмечаем все сообщения как прочитанные
        for msg in messages:
            if not msg.is_from_admin and not msg.read_at:
                msg.read_at = datetime.now()
        await session.commit()
        
        # Формируем текст с сообщениями
        messages_text = []
        for msg in messages:
            sender = "👨‍💼 Админ" if msg.is_from_admin else f"👤 {user.full_name}"
            messages_text.append(
                f"{sender} ({msg.created_at.strftime('%d.%m %H:%M')}):\n"
                f"{msg.message}"
            )
        
        ticket_info = (
            f"💬 <b>Тикет #{ticket.id}</b>\n\n"
            f"👤 Пользователь: {user.full_name}\n"
            f"🆔 Telegram ID: <code>{user.telegram_id}</code>\n"
            f"📞 Телефон: {user.phone}\n"
            f"📅 Создан: {ticket.created_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"🔄 Обновлен: {ticket.updated_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"📋 Статус: {ticket.status}\n\n"
            f"💬 <b>Сообщения ({len(messages)}):</b>\n\n"
        )
        
        if messages_text:
            ticket_info += "\n\n".join(messages_text)
        else:
            ticket_info += "Сообщений пока нет"
        
        ticket_info += (
            f"\n\n💡 <b>Для ответа используйте:</b>\n"
            f"<code>/ticket {ticket.id} Ваш ответ</code>"
        )
        
        await message.answer(ticket_info, parse_mode="HTML")


@router.message(Command("close_ticket"))
async def close_ticket(message: Message):
    """
    Закрыть тикет поддержки
    
    Формат: /close_ticket <ticket_id>
    """
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer(
            "❌ Укажите ID тикета\n\n"
            "Формат: <code>/close_ticket 1</code>",
            parse_mode="HTML"
        )
        return
    
    try:
        ticket_id = int(args[0])
    except ValueError:
        await message.answer("❌ Неверный формат ID тикета")
        return
    
    async with async_session() as session:
        result = await session.execute(
            select(SupportTicket, User)
            .join(User, SupportTicket.user_id == User.id)
            .where(SupportTicket.id == ticket_id)
        )
        ticket_data = result.first()
        
        if not ticket_data:
            await message.answer(f"❌ Тикет #{ticket_id} не найден")
            return
        
        ticket, user = ticket_data
        
        if ticket.status == "closed":
            await message.answer(f"ℹ️ Тикет #{ticket_id} уже закрыт")
            return
        
        ticket.status = "closed"
        ticket.updated_at = datetime.now()
        await session.commit()
        
        # Уведомляем пользователя
        try:
            notification_text = (
                f"✅ <b>Тикет #{ticket.id} закрыт</b>\n\n"
                f"Спасибо за обращение! Если у вас возникнут вопросы, создайте новый тикет."
            )
            await send_notification(user.telegram_id, notification_text)
        except Exception as e:
            print(f"⚠️ Ошибка отправки уведомления пользователю: {e}")
        
        await message.answer(
            f"✅ <b>Тикет закрыт</b>\n\n"
            f"📋 Тикет: #{ticket.id}\n"
            f"👤 Пользователь: {user.full_name}",
            parse_mode="HTML"
        )

