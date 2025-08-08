from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.contractor import Contractor
from bot.utils.state import StateUtils


router = Router()


@router.message(Contractor.confirmation)
async def show_contractor_summary(message: Message, state: FSMContext):
    """
    Обрабатывает введенные данные от пользователя в рамках формы Contractor.
    
    Args:
        message (Message): Входящее сообщение со сводкой от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)

    sent = await StateUtils.send_contractor_summary(message=message, data=data, for_admin=False)
    
    await state.update_data(last_bot_message=sent.message_id)