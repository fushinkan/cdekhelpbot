import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery


from app.api.handlers.user_info import get_contract_number_from_db
from app.api.handlers.normalize import normalize_phone
from bot.utils.exceptions import UserNotExistsException, IncorrectPhone
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from app.db.base import async_session_factory


router = Router()


@router.callback_query(F.data == "create_invoice")
async def get_contract_number(callback: CallbackQuery, state: FSMContext):
    """
    Автоматически подставляет номер договора в ответ боту из БД.
    """
    
    await callback.answer("Отлично! Давайте создадим накладную.")
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    phone_raw = data.get("phone")
    phone = await normalize_phone(phone_raw)
    
    
    async with async_session_factory() as session:
        try:
            contract_number = await get_contract_number_from_db(phone, session)


            await state.update_data(contract_number=contract_number)

            await state.set_state(InvoiceForm.departure_city)
            await StateUtils.push_state_to_history(state, InvoiceForm.departure_city)
            
            sent = await callback.message.edit_text("🏙 Пожалуйста, введите город отправления", reply_markup=await BackButtons.back_to_menu())
            await state.update_data(last_bot_message=sent.message_id, phone=phone)
    
        except (UserNotExistsException, IncorrectPhone) as e:
            sent = await callback.message.answer(str(e))
            await asyncio.sleep(2)
            await sent.delete()
            await callback.message.delete()