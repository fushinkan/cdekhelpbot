from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.contractor import Contractor
from bot.utils.state import StateUtils
from bot.utils.validate import Validator
from bot.utils.exceptions import IncorrectTinNumber
from bot.utils.bot_utils import BotUtils
from bot.utils.state import StateUtils


router = Router()


@router.message(Contractor.tin)
async def process_tin(message: Message, state: FSMContext):
    """
    Обрабатывает ввод ИНН пользователя в рамках формы Contractor.

    Args:
        message (Message): Входящее сообщение с ИНН от пользователя.
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе заполнения формы.
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    tin_number = message.text.strip()
    
    try:
        await Validator.correct_tin_number(text=tin_number)
        
        await state.update_data(tin_number=tin_number)
        
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await StateUtils.get_contractor_summary(message=message, data=data)

        await state.update_data(last_bot_message=sent.message_id)
        
    except IncorrectTinNumber as e:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
       
        sent = await message.answer(str(e), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        return