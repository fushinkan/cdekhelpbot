from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.state import StateUtils
from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.storage import AdminText, CustomerText

import asyncio
import httpx


router = Router()

pending_pdf_sends = {}  # key: manager_telegram_id, value: dict с info для отправки


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
        for_admin=True
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
        for_admin=True
    )
    
    sent = await callback.message.answer(CustomerText.AGREEMENT_ANSWER)
    
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
    
    pending_pdf_sends[callback.from_user.id] = {
        "user_id": user_id,
        "username": username
    }

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
        text=CustomerText.REJECT_ANSWER
    )

    await callback.answer("✅ Пользователь уведомлен об отмене.")
    await asyncio.sleep(5)
    await sent.delete()
    

@router.callback_query(F.data == "customers")
async def get_customers_pagination_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    Показывает всех клиентов у администратора с использованием пагинации.
    
    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    page = 1
    per_page = 10
    
    async with httpx.AsyncClient() as client:
        try:
            resp_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/telegram/{callback.from_user.id}")
            resp_user.raise_for_status()
            user_data = resp_user.json()
            
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
    text = AdminText.CONTRACTOR_LIST_TEXT.format(page=page, total_pages=total_pages, total=data.get("total"))
        
    keyboard = await AdminKeyboards.get_customers(
        clients=clients,
        page=page,
        total_pages=total_pages
    )
    
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
    
    await state.update_data(user_data=user_data)

    
@router.callback_query(F.data.startswith("forward_page_") | F.data.startswith("backward_page_"))
async def forward_or_backward_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает кнопки 'Вперед' и 'Назад' при просмотре клиентов.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = callback.data
    
    if data.startswith("forward_page_"):
        page = int(data.replace("forward_page_", ""))
    else:
        page = int(data.replace("backward_page_", ""))
        
    per_page = 10
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.BASE_FASTAPI_URL}/customers/all_customers",
                params={"page": page, "per_page": per_page}
            )
            
            response.raise_for_status()
        
        except httpx.HTTPError as e:
            await callback.answer(f"❌ Ошибка: {str(e)}", show_alert=True)
            return
        
    data = response.json()
    clients = data["users"]
    total_pages = data['total_pages']
    text = AdminText.CONTRACTOR_LIST_TEXT.format(page=page, total_pages=total_pages, total=data.get('total'))
        
    keyboard = await AdminKeyboards.get_customers(
        clients=clients,
        total_pages=total_pages,
        page=page
    )
        
    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

    await callback.answer()
    

@router.callback_query(F.data.startswith("client_"))
async def show_client_summary_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    Показывает информацию о конкретном клиенте.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    
    user_id = int(callback.data.split("_")[1])

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.BASE_FASTAPI_URL}/user/{user_id}"
            )
            
            response.raise_for_status()
        
        except httpx.HTTPError as e:
            await callback.message.answer("❌ Не удалось получить информацию о клиенте.")
            return
        
    user_data = response.json()

    phones_text = "\n".join(f"📞 {phone['number']}" for phone in user_data.get("phones", [])) or "📞 Нет номеров"
    
    message_text = AdminText.CONTRACTOR_DESCRIPTION.format(
        contractor=user_data["contractor"],
        city=user_data["city"],
        contract_number=user_data["contract_number"],
        phones_text=phones_text
    )
    
    await callback.message.edit_text(message_text, reply_markup=await AdminKeyboards.back_to_customers_with_history(), parse_mode="HTML")
    
    await state.update_data(user_data=user_data, selected_client_id=user_data["id"], role="admin")