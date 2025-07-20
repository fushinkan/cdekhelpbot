import asyncio

from aiogram.fsm.context import FSMContext
from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.states.invoice import InvoiceForm, INVOICE_PROMPTS, STATE_MAP
from bot.keyboards.backbuttons import BackButtons
from bot.utils.invoice import StateUtils


router = Router()


@router.callback_query(F.data == "no")
async def no_extra_services(callback: CallbackQuery, state: FSMContext):
    """
    Отправляет сводку без дополнительных услуг и переводит пользователя в состояние подтверждения.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)  
    sent = await StateUtils.get_summary(message=callback.message, data=data)
    
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(last_bot_message=sent.message_id)
    
    
@router.callback_query(F.data == "back_to_summary")
async def back_to_summary(callback: CallbackQuery, state: FSMContext):
    """
    Возвращает пользователя к полной сводке при нажатии кнопки 'Назад' и сбрасывает режим редактирования.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
        
    await state.set_state(InvoiceForm.confirmation)
    await state.update_data(editing_field=None)

    await StateUtils.get_summary(message=callback.message, data=data)


@router.callback_query(F.data.startswith("edit_"))
async def edit_invoice(callback: CallbackQuery, state: FSMContext):
    """
    Обрабатывает запрос на изменение выбранного пункта, отправляет пользователю соответствующий запрос и переводит в нужное состояние.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """

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
    
    
@router.callback_query(F.data == "confirm")
async def send_invoice_summary(callback: CallbackQuery, state: FSMContext):
    """
    Отправляет итоговую сводку менеджеру и уведомляет пользователя об успешной отправке данных.

    Args:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Текущее состояние FSM и данные пользователя.
    """
    
    data = await StateUtils.prepare_next_state(obj=callback, state=state)
    data["user_full_name"] = callback.from_user.username
    
    await StateUtils.send_summary(
        message=callback,
        data=data,
        chat_id=-1002716160058
    )
    
    await callback.answer("✅ Данные отправлены менеджеру.")
    