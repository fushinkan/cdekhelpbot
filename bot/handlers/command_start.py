import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatAction
from aiogram import filters, types
from aiogram import Router

from bot.keyboards.basic import BasicKeyboards

router = Router()


@router.message(filters.CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Обработчик команды /start. Отправляет приветственное сообщение и предлагает действия.
    
    Показывает кнопки:
        - Войти (начать процесс авторизации)
        - Помощь (информация о возможностях бота)
    """
    
    await state.clear()
    
    
    welcoming_text = (
        "👋 Привет!\n\n"
        "Я — электронный помощник менеджера по продажам СДЭК.\n\n"
        "Работаю по адресу:\n" 
        "Липецкая область, г. Данков,\n 1-й Спортивный переулок, 3\n\n"
        "Выбери нужный пункт меню, чтобы начать работу."
    )
    
    
    await message.bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(1)    
    
    
    await message.answer(welcoming_text, reply_markup=await BasicKeyboards.get_welcoming_kb())
    
    
    await asyncio.sleep(1)
    await message.delete()
