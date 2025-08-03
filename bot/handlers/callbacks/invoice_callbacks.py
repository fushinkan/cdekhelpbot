from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.states.invoice import InvoiceForm
from bot.utils.state import StateUtils
from bot.handlers.authorization.main_menu import proceed_to_main_menu


router = Router()


@router.callback_query(F.data == "no")
async def no_extra_services(callback: CallbackQuery, state: FSMContext):
    """
    Отправляет сводку без дополнительных услуг и переводит пользователя в состояние подтверждения.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)  
    sent = await StateUtils.get_summary(message=callback.message, data=data)
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(last_bot_message=sent.message_id)
    

@router.callback_query(F.data == "cancel")
async def no_extra_services(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Отмена' возвращает пользователя в его профиль

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state) 
     
    await proceed_to_main_menu(role=data.get('role'), user_data=data, message=callback.message)