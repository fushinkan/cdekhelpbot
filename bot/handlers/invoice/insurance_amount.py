import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message



from bot.utils.validate import InvoiceValidator
from bot.utils.exceptions import IncorrectInsurance
from bot.utils.delete_messages import delete_prev_messages
from bot.states.invoice import InvoiceForm
from bot.keyboards.customer import CustomerKeyboards



router = Router()


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
    