import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.api.handlers.normalize import normalize_phone
from bot.states.invoice import InvoiceForm, INVOICE_PROMPTS, STATE_MAP
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()

    
@router.callback_query(F.data.startswith("go_back_to_"))
async def go_back(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик для отката состояний.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    
    
    await asyncio.sleep(0.3)
    
    
    prev_state = await StateUtils.pop_state_from_history(state)
    
    if prev_state is None:
        phone_raw = data.get("phone")
        phone = await normalize_phone(phone_raw)
        
        
        await asyncio.sleep(0.2)
        await state.clear()
        await state.update_data(phone=phone)
    
        main_menu = (
            "👋 Приветствую!\n\n"
            "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
            "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
            "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
        )
    
    
        await callback.message.edit_text(main_menu, reply_markup=await CustomerKeyboards.customer_kb())
        return 
    
    await state.set_state(prev_state)
    
    
    prompt = INVOICE_PROMPTS.get(prev_state.state)
    if prompt is None:
        await callback.answer("⚠️ Попробуйте заново ввести данные.")
        return
    
    
    text, keyboard_coroutine = prompt
    keyboard = await keyboard_coroutine()
    sent = await callback.message.edit_text(text, reply_markup=keyboard)
    
    
    await state.update_data(last_bot_message=sent.message_id)
    

@router.callback_query(F.data == "no")
async def no_extra_services(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик присылает сводку без дополнительных услуг.
    """
    
    data = await StateUtils.prepare_next_state(callback, state)

    
    
    sent = await StateUtils.get_summary(callback.message, data)
    
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.callback_query(F.data == "back_to_summary")
async def back_to_summary(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' в изменении пунктов, откатывает пользователя до полной сводки.
    """
    
    data = await StateUtils.prepare_next_state(callback, state)
        
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(editing_field=None)


    await StateUtils.get_summary(callback.message, data)
    #await callback.message.edit_text(sent, reply_markup=await CustomerKeyboards.edit_or_confirm(), parse_mode="HTML")


@router.callback_query(F.data.startswith("edit_"))
async def edit_invoice(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Изменить <пункт>' перезаписывает данные в состояние и динамически изменяет сводку
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
    
    

    