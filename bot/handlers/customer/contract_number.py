from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.utils.state import StateUtils
from bot.utils.validate import Validator

from bot.utils.exceptions import IncorrectAgreementException
from bot.states.customer import Customer
from bot.keyboards.backbuttons import BackButtons


router = Router()
    
    
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