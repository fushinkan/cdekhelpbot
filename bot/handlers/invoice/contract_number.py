import httpx
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery


from app.core.config import settings
from app.api.handlers.get_user import UserInDB
from app.api.utils.normalize import normalize_phone
from bot.utils.exceptions import UserNotExistsException, IncorrectPhoneException
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.state import StateUtils

import asyncio


router = Router()


@router.callback_query(F.data == "create_invoice")
async def get_contract_number(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки 'create_invoice'.

    Автоматически получает и подставляет номер договора из базы данных для дальнейшей работы с ботом.

    Args:
        callback (CallbackQuery): Объект callback-запроса от Telegram при нажатии кнопки.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя.
    """
    
    await callback.answer("Отлично! Давайте создадим накладную.")
    await asyncio.sleep(0.2)
    
    data = await state.get_data()
    phone_raw = data.get("phone")
    phone_number = await normalize_phone(phone=phone_raw)
    
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{settings.BASE_FASTAPI_URL}/user/phone/{phone_number}"
            )
            
            response.raise_for_status()
            user_data = response.json()
            
            contract_number = user_data.get("contract_number")
            await state.update_data(contract_number=contract_number)
            await state.set_state(InvoiceForm.departure_city)
            await StateUtils.push_state_to_history(state=state, new_state=InvoiceForm.departure_city)

            sent = await callback.message.edit_text(
                "🏙 Пожалуйста, введите город отправления",
                reply_markup=await BackButtons.back_to_menu()
            )
            await state.update_data(last_bot_message=sent.message_id)

        except (UserNotExistsException, IncorrectPhoneException) as e:
            sent = await callback.message.answer(str(e))
            await asyncio.sleep(2)
            await sent.delete()
            await callback.message.delete()

        except httpx.HTTPError:
            sent = await callback.message.answer("❌ Ошибка при получении данных. Попробуйте позже.")
            await asyncio.sleep(2)
            await sent.delete()
            await callback.message.delete()  