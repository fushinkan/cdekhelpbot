import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.backbuttons import BackButtons

from bot.states.admin import AdminAuth

router = Router()


@router.callback_query(F.data == "enter")
async def process_phone(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Войти' просим пользователя отправить номер телефона.
    """

    
    await asyncio.sleep(0.2)
    await callback.answer()
    
    
    sent = await callback.message.edit_text("Отправь свой номер телефона для авторизации.", reply_markup=await BackButtons.back_to_welcoming_screen())
    
    
    await state.set_state(AdminAuth.waiting_for_phone)
    await state.update_data(last_bot_message=sent.message_id)