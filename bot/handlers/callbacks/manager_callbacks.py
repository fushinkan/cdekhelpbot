from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.state import StateUtils
from bot.states.send_invoice import SendInvoice
from bot.keyboards.admin import AdminKeyboards

import asyncio
import httpx


router = Router()


@router.callback_query(F.data == "confirm")
async def send_invoice_summary(callback: CallbackQuery, state: FSMContext):
    """
    Отправляет итоговую сводку менеджеру и уведомляет пользователя об успешной отправке данных.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    data["user_full_name"] = callback.from_user.username
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username

    await state.update_data(**data)
    
    await StateUtils.send_summary(
        message=callback,
        data=data,
        chat_id=settings.INVOICE_CHAT_ID
    )
    
    await callback.answer("✅ Данные отправлены менеджеру.")
    
    
@router.callback_query(F.data == "allow_agreement")
async def send_contractor_summary(callback: CallbackQuery, state: FSMContext):
    """
    Отправляет итоговую сводку менеджеру и уведомляет пользователя об успешной отправке данных.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    data["user_id"] = callback.from_user.id
    data["username"] = callback.from_user.username

    await StateUtils.send_contractor_summary(
        message=callback,
        data=data,
        chat_id=settings.INVOICE_CHAT_ID
    )
    
    sent = await callback.message.answer(
        (f"📩 Данные успешно переданы менеджеру!\n"
        f"С вами свяжутся в течение 1–2 рабочих дней для уточнения деталей и заключения договора.\n"
        f"Благодарим за обращение!")
    )
    
    await asyncio.sleep(15)
    
    await sent.delete()
    
    
@router.callback_query(F.data.startswith("answer_to_client:"))
async def handle_answer_invoice(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает ожидание ответа в виде PDF-файла.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    user_id = int(callback.data.split(":")[1])
    username = callback.data.split(":")[2]
    
    sent = await callback.message.edit_text(
        text="📎 Пришлите PDF-файл с накладной для клиента.",
    )
    
    await state.set_state(SendInvoice.waiting_for_invoice)
    await state.update_data(user_id=user_id, username=username, last_bot_message=sent.message_id)

    await callback.answer()
    
    
@router.callback_query(F.data.startswith("reject_answer:"))
async def reject_invoice(callback: CallbackQuery, state: FSMContext):
    """
    Отменяет создание накладной.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    user_id = callback.data.split(":")[1]

    sent = await callback.message.bot.send_message(
        chat_id=user_id,
        text=(
            "❌ Ваш запрос был отменен.\n"
            "Если нужна помощь, пожалуйста, свяжитесь с нами по номеру +7 (904)-280-30-01"
        )
    )

    await callback.answer("✅ Пользователь уведомлен об отмене.")
    

@router.callback_query(F.data == "customers")
async def get_customers_pagination_bot_handler(callback: CallbackQuery, state: FSMContext):
    
    page = 1
    per_page = 10
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.BASE_FASTAPI_URL}/customers/all_customers",
                params={"page": page, "per_page": per_page}
            )
            
            response.raise_for_status()
            
        except httpx.HTTPError as e:
            sent = await callback.message.answer(f"❌ Ошибка при получении клиентов: {str(e)}")
            return
    
    data = response.json()
    clients = data["users"]
    total_pages = data["total_pages"]
        
    keyboard = await AdminKeyboards.get_customers(
        clients=clients,
        page=page,
        total_pages=total_pages
    )
    
    await callback.message.edit_text(
       " 👥 Все клиенты, обслуживаемые отделом продаж в городе Данков, по адресу: 1-й Спортивный переулок, 3",
       reply_markup=keyboard
    )