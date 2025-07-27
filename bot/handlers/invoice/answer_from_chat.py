from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.db.base import async_session_factory
from app.api.handlers.save_invoice import save_invoice
from app.api.handlers.get_user import UserInDB
from bot.states.send_invoice import SendInvoice


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
    data = await state.get_data()
    user_id = data.get("user_id")
    username = data.get("username")
    
    document = message.document
    file_name = document.file_name

    
    try:
        parts = file_name.replace(".pdf", "").split("-")
        departure_city, recipient_city, invoice_number = parts
    except Exception:
        return await message.answer("Название файла, должно быть в формате Откуда-Куда-НомерНакладной")
    
    if document.mime_type != "application/pdf":
        return await message.answer("❗ Пожалуйста, отправьте файл в формате PDF.")

    async with async_session_factory() as session:
        user = await UserInDB.get_client_by_telegram_id(telegram_id=user_id, session=session)
        
        await save_invoice(
            user_id=user.id,
            departure_city=departure_city,
            recipient_city=recipient_city,
            invoice_number=invoice_number,
            telegram_file_id=document.file_id,
            session=session
        )

        await session.commit()
        
    await message.bot.send_document(
        chat_id=user_id,
        document=document.file_id,
        caption="📄 Ваша накладная готова!"
    )

    await message.answer(f"✅ Накладная успешно отправлена пользователю @{username}")
    await state.clear()