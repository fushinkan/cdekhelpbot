from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.states.contractor import Contractor
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.callback_query(F.data == "create_agreement")
async def process_phone_contractor(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Заключить договор' опрашивает пользователя для создания договора.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """

    sent = await callback.message.edit_text("📱 Введите номер телефона", reply_markup=await BackButtons.back_to_welcoming_screen())
    await state.update_data(last_bot_message=sent.message_id)
    await state.set_state(Contractor.phone)