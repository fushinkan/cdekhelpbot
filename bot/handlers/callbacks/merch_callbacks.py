from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.backbuttons import BackButtons
from bot.states.merch import Merch
from bot.utils.storage import CustomerText


router = Router()


@router.callback_query(F.data == "get_merch")
async def start_merch(callback: CallbackQuery, state: FSMContext):
    """
    По кнпоке 'Получить мерч' запрашивает у пользователя ИНН для связи.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """    
    
    sent = await callback.message.edit_text(CustomerText.MERCH_TEXT, reply_markup=await BackButtons.back_to_menu(), parse_mode="HTML")
    
    await state.set_state(Merch.tin)
    await state.update_data(last_bot_message=sent.message_id)
    await callback.answer()