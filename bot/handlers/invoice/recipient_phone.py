from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import Message

from bot.utils.validate import InvoiceValidator
from bot.utils.exceptions import IncorrectPhone
from bot.states.invoice import InvoiceForm
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils
from bot.utils.delete_messages import delete_prev_messages

router = Router()


@router.message(InvoiceForm.recipient_phone)
async def get_recipient_phone(message: Message, state: FSMContext):
    """
    Обработчик для получения номера телефона получателя.
    """
        
    data = await StateUtils.prepare_next_state(message, state)


    recipient_phone = message.text.strip()
    await state.update_data(recipient_phone=recipient_phone)

    try:
        await InvoiceValidator.correct_phone(recipient_phone)
    except IncorrectPhone as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        
        await state.update_data(error_message=sent.message_id)
        return 


    if data.get("editing_field"):
        await state.update_data(editing_field=None)
        updated_data = await state.get_data()
        updated_summary = await StateUtils.get_summary(message, updated_data)
        await state.update_data(last_bot_message_id=updated_summary.message_id)
        await delete_prev_messages(message, updated_data.get("last_bot_message_id"))
        return
        
        
    data = await state.get_data()
    error_message = data.get("error_message")
    try:
        if error_message:
            await delete_prev_messages(message, error_message)      
    except TelegramBadRequest:
        pass

    await state.set_state(InvoiceForm.recipient_city)
    await StateUtils.push_state_to_history(state, InvoiceForm.recipient_city)
        
        
    sent = await message.answer("🌆 Пожалуйста, укажите город получателя для доставки", reply_markup=await BackButtons.back_to_recipient_phone())

        
    await state.update_data(last_bot_message=sent.message_id)
        