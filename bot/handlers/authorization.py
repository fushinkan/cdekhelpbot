import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message

from api.handlers.normalize import normalize_phone
from api.utils.security import verify_password
from bot.utils.exceptions import UserNotExistsException, IncorrectPhone, IncorrectPasswordException
from bot.keyboards.admin import AdminKeyboards
from bot.keyboards.customer import CustomerKeyboards
from bot.keyboards.basic import BasicKeyboards
from bot.keyboards.backbuttons import BackButtons
from bot.utils.fetch_user import fetch_user_by_phone
from bot.utils.delete_messages import delete_prev_messages
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


@router.message(AdminAuth.waiting_for_phone)
async def process_role(message: Message, state: FSMContext):
    """
    Проверяет роль пользователя.
    
    Если роль админ, то запрашивает его пароль.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    
    
    try:
        phone = await normalize_phone(message.text)
        user = await fetch_user_by_phone(phone)     
        await delete_prev_messages(message, message_id=last_bot_message_id)
        await message.delete()
        
    except (IncorrectPhone, UserNotExistsException) as e:
        sent = await message.answer(str(e), parse_mode="HTML")
        await asyncio.sleep(2)
        await message.delete()
        await sent.delete()
        return
    
    
    await state.update_data(phone=phone)
    
    
    if user.role == "admin":
        sent = await message.answer("Пожалуйста, введите ваш пароль для подтверждения доступа.", reply_markup=await BackButtons.back_to_phone())
        await state.set_state(AdminAuth.waiting_for_password)
        await state.update_data(last_bot_message=sent.message_id)
        await asyncio.sleep(2)
    else:
        sent = await message.answer("Вы успешно вошли! Рекомендуется установить пароль для безопасности.", reply_markup=await CustomerKeyboards.password_kb())
        await state.update_data(last_bot_message=sent.message_id)
        await asyncio.sleep(2)


@router.message(AdminAuth.waiting_for_password)
async def process_password(message: Message, state: FSMContext):
    """
    Проверяет корректность введенного пароля.
    """
    
    await asyncio.sleep(0.2)
    
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
    phone = data.get("phone")
    user = await fetch_user_by_phone(phone)
    entered_password = message.text.strip()
    
       
    await delete_prev_messages(message, last_bot_message_id)
        
        
    if not verify_password(entered_password, user.hashed_psw):
        sent = await message.answer(IncorrectPasswordException.__doc__)
        await asyncio.sleep(2)
        await message.delete()
        await sent.delete()
        return
    
    
    await message.delete()
    

    await message.answer((
        f"👋 Здравствуйте, {user.contractor}\n\n"
        "Добро пожаловать в панель управления.\n"
        "Здесь вы можете управлять пользователями и контролировать систему.\n"
        "Выберите нужный пункт меню, чтобы начать работу."
    ), reply_markup=await AdminKeyboards.get_admin_kb())
    
    
    await state.clear()
    
    
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
    
    
    await callback.message.edit_text("Отправь свой номер телефона для авторизации.", reply_markup=await BasicKeyboards.back_to_welcoming_screen())
    
    
    await state.set_state(AdminAuth.waiting_for_phone)
    

@router.callback_query(F.data.in_(["continue", "cancel"]))
async def without_password(callback: CallbackQuery, state: FSMContext):
    """
    По кнопке 'Продолжить' переводит пользователя в его профиль и рекомендует поставить пароль.
    """
    
    data = await state.get_data()
    last_bot_message_id = data.get("last_bot_message")
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