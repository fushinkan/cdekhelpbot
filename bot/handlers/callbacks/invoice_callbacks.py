from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.states.invoice import InvoiceForm
from bot.utils.state import StateUtils
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.keyboards.backbuttons import BackButtons

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
    sent = await StateUtils.send_summary(message=callback.message, data=data, for_admin=False)
    
    await state.update_data(last_bot_message=sent.message_id)
    


@router.callback_query(F.data == "yes")
async def yes_extra_services(callback: CallbackQuery, state: FSMContext):
    """
    Собирает информацию о дополнительных услугах.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)  
    sent = await callback.message.answer("🛠️ Пожалуйста, введите дополнительные услуги", reply_markup=await BackButtons.back_to_insurance_amount())
    
    await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.extra_services)
    await state.set_state(InvoiceForm.extra_services)
    
    await state.update_data(last_bot_message=sent.message_id)
    
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel_extra_services(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Отмена' возвращает пользователя в его профиль

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state) 
     
    await proceed_to_main_menu(user_data=data, message=callback.message, state=state)