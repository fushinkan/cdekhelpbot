import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from app.api.handlers.normalize import normalize_phone
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.backbuttons import BackButtons
from bot.keyboards.basic import BasicKeyboards
from bot.states.admin import AdminAuth

router = Router()


@router.callback_query(F.data == "enter")
async def process_phone(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Войти' просим пользователя отправить номер телефона.
    """

    
    await asyncio.sleep(0.2)
    await callback.answer()
    
    
    sent = await callback.message.edit_text("Отправь свой номер телефона для авторизации.", reply_markup=await BackButtons.back_to_welcoming_screen())
    
    
    await state.set_state(AdminAuth.waiting_for_phone)
    await state.update_data(last_bot_message=sent.message_id)

    
@router.callback_query(F.data == "back_to_welcoming_screen")
async def back_to_welcoming_screen(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' возвращает на меню приветствия.
    """
    
    await asyncio.sleep(0.2)
    await state.clear()
    
    
    welcoming_text = (
        "👋 Привет!\n\n"
        "Я — электронный помощник менеджера по продажам СДЭК.\n\n"
        "Работаю по адресу:\n" 
        "Липецкая область, г. Данков,\n 1-й Спортивный переулок, 3\n\n"
        "Выбери нужный пункт меню, чтобы начать работу."
    )
    
    
    await callback.message.edit_text(welcoming_text, reply_markup=await BasicKeyboards.get_welcoming_kb())


@router.callback_query(F.data == "back_to_phone")
async def back_to_phone_screen(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Назад' возвращает пользователя ко вводу номера телефона.
    """
    
    await asyncio.sleep(0.2)
    await callback.answer()
    await state.clear()
    
    
    await callback.message.edit_text("Отправь свой номер телефона для авторизации.", reply_markup=await BackButtons.back_to_welcoming_screen())
    
    
    await state.set_state(AdminAuth.waiting_for_phone)
    

@router.callback_query(F.data.in_(["continue", "cancel"]))
async def without_password(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Продолжить' переводит пользователя в его профиль и рекомендует поставить пароль.
    """
    
    data = await state.get_data()
    #last_bot_message_id = data.get("last_bot_message")
    phone_raw = data.get("phone")
    phone = await normalize_phone(phone_raw)


    await asyncio.sleep(0.2)    
    await callback.answer("Для безопасности установите пароль!")
    
    
    await callback.message.edit_text((
        "👋 Приветствую!\n\n"
        "Здесь ты можешь быстро оформить накладную, подобрать тарифы и подключить дополнительные услуги. 🚀\n"
        "Не нужно ломать голову — просто выбери, что нужно, и я всё сделаю быстро и без лишних хлопот! 💼✨\n"
        "Если возникнут вопросы — пиши, всегда рад помочь! 😊👍"
    ), reply_markup=await CustomerKeyboards.customer_kb())
    
    
    await asyncio.sleep(1)
    #await delete_prev_messages(callback, last_bot_message_id)
    await state.clear()
    await state.update_data(phone=phone)