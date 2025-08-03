from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from app.api.utils.normalize import Normalize
from bot.handlers.authorization.main_menu import proceed_to_main_menu
from bot.utils.state import StateUtils
from bot.utils.validate import Validator
from bot.utils.bot_utils import BotUtils
from bot.utils.exceptions import IncorrectAgreementException, IncorrectPhoneException
from bot.states.customer import Customer
from bot.keyboards.backbuttons import BackButtons

import httpx


router = Router()


@router.callback_query(F.data == "add_contractor")
async def add_contractor_bot_handler(callback: CallbackQuery, state: FSMContext):
    """
    Добаление клиента в таблицу Users.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    role = "admin"
    
    if await StateUtils.edit_invoice_or_data(data=data, message=callback.message, state=state):
        return
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.contractor)
    await state.set_state(Customer.contractor)
    sent = await callback.message.answer("👤 Введите имя контрагента", reply_markup=await BackButtons.back_to_admin_panel())
    
    await state.update_data(last_bot_message=sent.message_id, role=role)
    await callback.answer()


@router.message(Customer.contractor)
async def contractor_handler(message: Message, state: FSMContext):
    """
    Обработчик наименования для контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    contractor = message.text.title()
    
    await state.update_data(contractor=contractor)
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.city)
    await state.set_state(Customer.city)
    
    sent = await message.answer("🏙 Введите город контрагента", reply_markup=await BackButtons.back_to_customer_contractor())
    await state.update_data(last_bot_message=sent.message_id)


@router.message(Customer.city)
async def customer_city_handler(message: Message, state: FSMContext):
    """
    Обработчик города для контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    city = message.text.title()
    
    await state.update_data(city=city)
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.contract_number)
    await state.set_state(Customer.contract_number)
    sent = await message.answer("📄 Введите номер договора (например, KU-ABC7-123)", reply_markup=await BackButtons.back_to_customer_city())
    
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.message(Customer.contract_number)
async def contract_number_handler(message: Message, state: FSMContext):
    """
    Обрабатывает введенный номер договора контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    contract_number = message.text.upper()
    
    await state.update_data(contract_number=contract_number)
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    if not await Validator.correct_agreement_validator(text=contract_number):
        sent = await message.answer(str(IncorrectAgreementException(IncorrectAgreementException.__doc__)), parse_mode="HTML")
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        
        await state.update_data(error_message=sent.message_id)
        return
    
    await StateUtils.push_state_to_history(state=state, new_state=Customer.number)
    await state.set_state(Customer.number)
    
    sent = await message.answer("📱 Введите номера телефонов через запятую (например, 89042803001, 89991234567)", reply_markup=await BackButtons.back_to_customer_contract_number())
    
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.message(Customer.number)
async def customer_number_handler(message: Message, state: FSMContext):
    """
    Обрабатывает номер(а) телефонов для контрагента.

    Args:
        message (Message): Входящее сообщение с названием города от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием контрагента в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return
    
    phones = [num.strip() for num in message.text.split(",") if num.strip()]
    normalized_phones = []
    
    try:
        for phone in phones:
            normalized = await Normalize.normalize_phone(phone=phone)
            normalized_phones.append(normalized)
    
    except IncorrectPhoneException as e:
        data = await StateUtils.prepare_next_state(obj=message, state=state)
        sent = await message.answer(str(e))
        
        await state.update_data(error_message=sent.message_id)
        return
    
    await state.update_data(phone=", ".join(normalized_phones))
    data = await StateUtils.prepare_next_state(obj=message, state=state)

    await StateUtils.show_customer_summary(data=data, message=message)


@router.callback_query(F.data == "admin_panel")
async def admin_panel(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает менеджера к админской панели

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    role = data.get("role", "admin")
    user_data = data
    
    await state.clear()
    
    await proceed_to_main_menu(role=role, user_data=user_data, message=callback.message)
    await callback.answer()
    

@router.callback_query(F.data == "customer_summary")
async def show_customer_summary(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает менеджера к сводке с новым контрагентом

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
        
    await StateUtils.show_customer_summary(data=data, message=callback.message)

    await callback.answer()
