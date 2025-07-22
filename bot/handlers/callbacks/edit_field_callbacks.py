import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.states.contractor import CONTRACTOR_PROMPTS, STATE_CONTRACTOR_MAP
from bot.states.invoice import  INVOICE_PROMPTS, STATE_MAP
from bot.keyboards.backbuttons import BackButtons


router = Router()


@router.callback_query(F.data.startswith("edit_"))
async def edit_invoice(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает запрос на изменение выбранного пункта, отправляет пользователю соответствующий запрос и переводит в нужное состояние.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """

    await asyncio.sleep(0.2)
    await callback.answer()
    
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


@router.callback_query(F.data.startswith("editt_contractor_"))
async def edit_contractor_summary(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает запрос на изменение выбранного пункта, отправляет пользователю соответствующий запрос и переводит в нужное состояние.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """

    await asyncio.sleep(0.2)
    await callback.answer()
    
    field = callback.data.removeprefix("editt_contractor_")
    new_state = STATE_CONTRACTOR_MAP.get(field)
    
    if not new_state:
        await callback.answer("❌ Неизвестное поле для редактирования.")
        return
    
    prompt, _ = CONTRACTOR_PROMPTS.get(new_state.state)
    keyboard = await BackButtons.back_to_contractor_summary()
    
    await callback.message.edit_text(prompt, reply_markup=keyboard)
    
    await state.set_state(new_state)
    await state.update_data(editing_field=field)