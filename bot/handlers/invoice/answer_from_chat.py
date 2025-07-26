from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

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

    if document.mime_type != "application/pdf":
        return await message.answer("❗ Пожалуйста, отправьте файл в формате PDF.")

    await message.bot.send_document(
        chat_id=user_id,
        document=document.file_id,
        caption="📄 Ваша накладная готова!"
    )

    await message.answer(f"✅ Накладная успешно отправлена пользователю @{username}")
    await state.clear()