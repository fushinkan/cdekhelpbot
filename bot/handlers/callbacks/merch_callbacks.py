from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.backbuttons import BackButtons
from bot.states.merch import Merch


router = Router()


@router.callback_query(F.data == "get_merch")
async def start_merch(callback: CallbackQuery, state: FSMContext):
    """
    По кнпоке 'Получить мерч' запрашивает у пользователя ИНН для связи.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    text = (
        """
        🎁 <b>Получи мерч, пригласив друга/партнёра по бизнесу заключить с нами договор как <i>САМОЗАНЯТОЕ ЛИЦО/ИП/ООО</i>!</b>\n
        📄 Пришли <b>ИНН</b>, свяжемся с заявкой в течении <u>24 часов</u>.\n\n
        ✅ В случае удачной заявки, свяжемся с вами, чтобы договориться о <b>адресе получения мерча</b>.
        """
    )
    
    sent = await callback.message.edit_text(text, reply_markup=await BackButtons.back_to_menu(), parse_mode="HTML")
    
    await state.set_state(Merch.tin)
    await state.update_data(last_bot_message=sent.message_id)
    await callback.answer()