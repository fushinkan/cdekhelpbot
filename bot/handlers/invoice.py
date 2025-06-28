import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery


from app.api.handlers.user_info import get_contract_number_from_db
from app.api.handlers.normalize import normalize_phone
from bot.utils.validate import InvoiceValidator
from bot.utils.exceptions import UserNotExistsException, IncorrectPhone, IncorrectInsurance, IncorrectAgreement
from bot.utils.delete_messages import delete_prev_messages
from bot.states.invoice import InvoiceForm, INVOICE_PROMPTS, STATE_MAP
from bot.keyboards.customer import CustomerKeyboards
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
            
            await state.set_state(InvoiceForm.contract_number)
            await state.update_data(contract_number=contract_number)
            await StateUtils.push_state_to_history(state, InvoiceForm.contract_number)
            
            await state.set_state(InvoiceForm.departure_city)
            await StateUtils.push_state_to_history(state, InvoiceForm.departure_city)
            
            sent = await callback.message.edit_text("🏙 Пожалуйста, введите город отправления", reply_markup=await BackButtons.back_to_menu())
            await state.update_data(last_bot_message=sent.message_id, phone=phone)
    
        except (UserNotExistsException, IncorrectPhone) as e:
            sent = await callback.message.answer(str(e))
            await asyncio.sleep(2)
            await sent.delete()
            await callback.message.delete()


@router.message(InvoiceForm.departure_city)
async def get_departure_city(message: Message, state: FSMContext):
    """
    Обработчик для получения города отправления.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    departure_city = message.text.strip()
    
    
    await asyncio.sleep(0.3)
    await message.delete()
    
    await delete_prev_messages(message, last_bot_message_id)
    
    
    await state.update_data(departure_city=departure_city)
    await state.set_state(InvoiceForm.departure_address)
    await StateUtils.push_state_to_history(state, InvoiceForm.departure_address)
    
    
    sent = await message.answer("📍 Отлично! Теперь введите адрес отправления/забора груза 🏠", reply_markup=await BackButtons.back_to_departure_city())
    
    
    await state.update_data(last_bot_message=sent.message_id)


@router.message(InvoiceForm.departure_address)
async def get_departure_address(message: Message, state: FSMContext):
    """
    Обработчик для адреса отправления.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    departure_address = message.text.strip()
    
    
    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id)
    
    
    await state.update_data(departure_address=departure_address)
    await state.set_state(InvoiceForm.recipient_phone)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_phone)
    
    
    sent = await message.answer("📱 Введите номер телефона получателя", reply_markup=await BackButtons.back_to_departure_address())
    
    
    await state.update_data(last_bot_message=sent.message_id)


@router.message(InvoiceForm.recipient_phone)
async def get_recipient_phone(message: Message, state: FSMContext):
    """
    Обработчик для получения номера телефона получателя.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    recipient_phone = message.text.strip()

    try:
        await InvoiceValidator.correct_phone(recipient_phone)
    except IncorrectPhone as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await asyncio.sleep(5)
        await message.delete()
        await sent.delete()
        return 
    
    
    await asyncio.sleep(1)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id)   
    
    
    await state.update_data(recipient_phone=recipient_phone)
    await state.set_state(InvoiceForm.recipient_city)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_city)
    
    
    sent = await message.answer("🌆 Пожалуйста, укажите город получателя для доставки", reply_markup=await BackButtons.back_to_recipient_phone())

    
    await state.update_data(last_bot_message=sent.message_id)
    

@router.message(InvoiceForm.recipient_city)
async def get_recipient_city(message: Message, state: FSMContext):
    """
    Обработчик для поулчения города получателя.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    recipient_city = message.text.strip()


    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id) 
    
    
    await state.update_data(recipient_city=recipient_city)
    await state.set_state(InvoiceForm.recipient_address)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_address)
    
    
    sent = await message.answer("📍 Отлично! Теперь укажите адрес получения/доставки", reply_markup=await BackButtons.back_to_recipient_city())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.message(InvoiceForm.recipient_address)
async def get_recipient_address(message: Message, state: FSMContext):
    """
    Обработчик для получения адреса доставки.
    """
        
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    recipient_address = message.text.strip()


    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id) 
    
    
    await state.update_data(recipient_address=recipient_address)
    await state.set_state(InvoiceForm.insurance_amount)
    await StateUtils.push_state_to_history(state, InvoiceForm.insurance_amount)
    
    sent = await message.answer("🛡️ На какую сумму нужна страховка?", reply_markup=await BackButtons.back_to_recipient_address())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    

@router.message(InvoiceForm.insurance_amount)
async def get_insurance_amount(message: Message, state: FSMContext):
    """
    Обработчик для получения суммы страхования.
    """
            
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    insurance_amount = message.text.strip()


    try:
        await InvoiceValidator.correct_insurance(insurance_amount)
    except IncorrectInsurance as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await asyncio.sleep(5)
        await message.delete()
        await sent.delete()
        return 
    
    
    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id) 
    
    
    await state.update_data(insurance_amount=insurance_amount)
    await state.set_state(InvoiceForm.confirmation)
    sent = await message.answer("🛠️ Добавить доп. услуги к заказу?", reply_markup=await CustomerKeyboards.extra_services())
    
    
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.message(InvoiceForm.confirmation)
async def confirmation(message: Message, state: FSMContext):
    """
    Обработчик для подтверждения или изменения сводки.
    """
               
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")


    await asyncio.sleep(0.3)
    await message.delete()
    await delete_prev_messages(message, last_bot_message_id) 
    
    
    sent = await StateUtils.get_summary(message, data)
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.message()
async def edit_field_value(message: Message, state: FSMContext):
    data = await state.get_data()
    editing_field = data.get("editing_field")
    
    if not editing_field:
        # Пользователь не в режиме редактирования, просто игнорируем
        return
    
    new_value = message.text.strip()
    
    try:
        if editing_field == "recipient_phone":
            await InvoiceValidator.correct_phone(new_value)
        elif editing_field == "insurance_amount":
            await InvoiceValidator.correct_insurance(new_value)
        elif editing_field == "contract_number":
            await InvoiceValidator.correct_agreement(new_value)

    except (IncorrectPhone, IncorrectInsurance, IncorrectAgreement) as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await asyncio.sleep(5)
        await sent.delete()
        await message.delete()
        return  # Валидация не прошла — не меняем данные
    
    # Если всё хорошо — обновляем данные
    await state.update_data({editing_field: new_value})
    await state.update_data(editing_field=None)
    
    await message.delete()
    
    data = await state.get_data()
    sent = await StateUtils.get_summary(message, data)
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(last_bot_message=sent.message_id)
    
    
    
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
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
        
        
    await asyncio.sleep(0.3)
    await delete_prev_messages(callback, last_bot_message_id)
    
    
    sent = await StateUtils.get_summary(callback.message, data)
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.callback_query(F.data == "back_to_summary")
async def back_to_summary(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' в изменении пунктов, откатывает пользователя до полной сводки.
    """
    
    await asyncio.sleep(0.2)

    await callback.answer()
    
    
    data = await state.get_data()
        
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(editing_field=None)


    sent = await StateUtils.get_summary(callback.message, data)
    await callback.message.edit_text(sent.text, reply_markup=await CustomerKeyboards.edit_or_confirm(), parse_mode="HTML")

@router.callback_query(F.data.startswith("edit_"))
async def edit_invoice(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Изменить <пункт>' перезаписывает данные в состояние и динамически изменяет сводку
    """
    print(f"[edit_invoice] callback.data = {callback.data}")
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
    
    

    