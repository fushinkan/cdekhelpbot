from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message


from bot.utils.validate import Validator
from bot.utils.exceptions import IncorrectInsurance
from bot.utils.state import StateUtils
from bot.states.invoice import InvoiceForm
from bot.keyboards.customer import CustomerKeyboards
from bot.utils.bot_utils import BotUtils


router = Router()


@router.message(InvoiceForm.insurance_amount)
async def get_insurance_amount(message: Message, state: FSMContext):
    """
    Обрабатывает ввод суммы страхования от пользователя.

    Args:
        message (Message): Входящее сообщение с суммой страхования.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе оформления.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    insurance_amount = message.text.strip()
    await state.update_data(insurance_amount=insurance_amount)
    
    try:
        await Validator.correct_insurance(text=insurance_amount)
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        
    except IncorrectInsurance as e:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)

        return 
    
    if await StateUtils.edit_invoice_or_data(data=data, message=message, state=state):
        return

    await state.set_state(InvoiceForm.confirmation)
    
    sent = await message.answer("🛠️ Добавить доп. услуги к заказу?", reply_markup=await CustomerKeyboards.extra_services())
    
    await state.update_data(last_bot_message=sent.message_id)
    