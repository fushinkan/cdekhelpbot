import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.states.invoice import INVOICE_PROMPTS, STATE_MAP
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.callback_query(F.data.startswith("edit_"))
async def edit_invoice(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает нажатие кнопки 'Изменить <пункт>'.

    Перезаписывает соответствующие данные в состоянии пользователя и динамически обновляет сводку заказа.

    Args:
        callback (CallbackQuery): Объект callback-запроса от Telegram при нажатии кнопки.
        state (FSMContext): Контейнер для хранения и управления текущим состоянием пользователя.
    """
    
    await asyncio.sleep(0.2)
    
    field = callback.data.removeprefix("edit_")
    new_state = STATE_MAP.get(field)
    
    if not new_state:
        await callback.answer("❌ Неизвестное поле для редактирования.")
        return
    
    prompt, _ = INVOICE_PROMPTS.get(new_state.state)
    keyboard = await BackButtons.back_to_summary()
    
    await callback.message.edit_text(prompt, reply_markup=keyboard)
    
    await state.set_state(new_state)
    await state.update_data(editing_field=field)
