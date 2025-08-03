@router.callback_query(F.data.startswith("go_back_to_"))
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Откатывает пользователя к предыдущему состоянию в истории или к главному меню, если истории нет.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    
    await asyncio.sleep(0.3)
    
    prev_state = await StateUtils.pop_state_from_history(state=state)
    
    if prev_state is None:
        phone_raw = data.get("phone")
        phone = await Normalize.normalize_phone(phone=phone_raw)
        
        await asyncio.sleep(0.2)
        await state.clear()
        await state.update_data(phone=phone)
    
        main_menu = (
            "👋 Приветствую!\n\n"
            "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
            "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
            "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
        )

        await callback.message.answer(main_menu, reply_markup=await CustomerKeyboards.customer_kb())
        return 
    
    await state.set_state(prev_state)
    
    prompt = INVOICE_PROMPTS.get(prev_state.state)
    if prompt is None:
        await callback.answer("⚠️ Попробуйте заново ввести данные.")
        return
    
    text, keyboard_coroutine = prompt
    keyboard = await keyboard_coroutine()

    sent = await callback.message.answer(text, reply_markup=keyboard)

    await state.update_data(last_bot_message=sent.message_id)
    
    
    
    
    
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