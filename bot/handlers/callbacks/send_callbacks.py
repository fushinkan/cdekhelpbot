from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.utils.state import StateUtils
from bot.states.send_invoice import SendInvoice

import asyncio

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
    
    await StateUtils.send_summary(
        message=callback,
        data=data,
        chat_id=-1002716160058
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
    data["user_full_name"] = callback.from_user.username

    await StateUtils.send_contractor_summary(
        message=callback,
        data=data,
        chat_id=-1002716160058
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
    user_id = int(callback.data.split(":")[1])
    username = callback.data.split(":")[2]
    
    await callback.message.edit_text(
        text="📎 Пришлите PDF-файл с накладной для клиента.",
    )
    
    await state.set_state(SendInvoice.waiting_for_invoice)
    await state.update_data(user_id=user_id, username=username)

    await callback.answer()