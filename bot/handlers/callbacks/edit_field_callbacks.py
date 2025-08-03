import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.states.contractor import CONTRACTOR_PROMPTS, STATE_CONTRACTOR_MAP
from bot.states.invoice import  INVOICE_PROMPTS, STATE_MAP
from bot.states.customer import CUSTOMER_PROMPTS, CUSTOMER_STATE_MAP
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.callback_query(F.data.startswith("edit_"))
async def universal_edit_handler(callback: CallbackQuery, state: FSMContext):
    """
    Универсальный обработчик редактирования данных: invoice, contractor и customer.

    Args:
        callback (CallbackQuery): Callback-запрос от пользователя.
        state (FSMContext): Состояние FSM и данные пользователя.
    """

    await asyncio.sleep(0.2)
    await callback.answer()
    
    parts = callback.data.split("_", 2)  # edit_invoice_city → ['edit', 'invoice', 'city']
    if len(parts) != 3:
        await callback.answer("❌ Неверный формат данных.")
        return

    _, edit_type, field = parts

    # Определение карты состояний, подсказок и клавиатуры
    if edit_type == "invoice":
        state_map = STATE_MAP
        prompts = INVOICE_PROMPTS
        keyboard = await BackButtons.back_to_summary()
    elif edit_type == "contractor":
        state_map = STATE_CONTRACTOR_MAP
        prompts = CONTRACTOR_PROMPTS
        keyboard = await BackButtons.back_to_contractor_summary()
    elif edit_type == "customer":

        state_map = CUSTOMER_STATE_MAP
        prompts = CUSTOMER_PROMPTS
        keyboard = await BackButtons.back_to_customer_summary()
    else:
        await callback.answer("❌ Неизвестный тип редактирования.")
        return

    new_state = state_map.get(field)
    if not new_state:
        await callback.answer("❌ Неизвестное поле.")
        return

    prompt, _ = prompts.get(new_state, ("❓ Введите значение:", None))


    await callback.message.edit_text(prompt, reply_markup=keyboard)
    await state.set_state(new_state)
    await state.update_data(editing_field=field)
