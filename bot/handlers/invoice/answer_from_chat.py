import httpx
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.state import StateUtils
from bot.states.send_invoice import SendInvoice
from bot.utils.exceptions import IncorrectFileName
from bot.utils.bot_utils import BotUtils


router = Router()


@router.message(SendInvoice.waiting_for_invoice, F.document)
async def handle_invoice_upload(message: Message, state: FSMContext):
    """
    Отвечает пользователю файлом PDF из чата с менеджерами.

    Args:
        message (Message): Сводка приходящая от пользователя
        state (FSMContext): Контейнер для хранения и управления состоянием пользователя в процессе ответа в виде файла.

    Returns:
        Message: Предупреждает менеджера о том, что ответ должен быть в формате PDF
    """
    
    data = await StateUtils.prepare_next_state(obj=message, state=state)
    tg_id = data.get("user_id")
    username = data.get("username")
    
    document = message.document
    file_name = document.file_name

    
    try:
        parts = file_name.replace(".pdf", "").split("-")
        departure_city, recipient_city, invoice_number = parts
        data = await BotUtils.delete_error_messages(obj=message, state=state)
    except (IncorrectFileName, ValueError) as e:
        data = await BotUtils.delete_error_messages(obj=message, state=state)
        sent = await message.answer(str(IncorrectFileName(IncorrectFileName.__doc__)), parse_mode="HTML")
        await state.update_data(error_message=sent.message_id)
        
        return
        
    if document.mime_type != "application/pdf":
        return await message.answer("❗ Пожалуйста, отправьте файл в формате PDF.")

    async with httpx.AsyncClient() as client:
        try:
            response_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/telegram/{tg_id}")
            response_user.raise_for_status()
            user_data = response_user.json()

            response_save_invoice = await client.post(
                f"{settings.BASE_FASTAPI_URL}/invoices/save_invoice/{user_data['id']}",
                json={
                    "departure_city": departure_city,
                    "recipient_city": recipient_city,
                    "invoice_number": invoice_number,
                    "telegram_file_id": document.file_id
                }
            )
            
            response_save_invoice.raise_for_status()
            
        except httpx.HTTPError as e:
            await message.answer(str(e))
            return
        
    await message.bot.send_document(
        chat_id=tg_id,
        document=document.file_id,
        caption="📄 Ваша накладная готова!"
    )

    await message.answer(f"✅ Накладная успешно отправлена пользователю @{username}")
    await state.clear()