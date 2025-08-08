from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from bot.utils.state import StateUtils
from bot.utils.exceptions import IncorrectFileNameException
from bot.states.send_invoice import SendInvoice
from bot.handlers.callbacks.manager_callbacks import pending_pdf_sends

import httpx


router = Router()


@router.message(F.document.mime_type == "application/pdf")
async def handle_invoice_upload(message: Message):
    manager_id = message.from_user.id
    if manager_id not in pending_pdf_sends:
        return await message.answer("❗ У вас нет активной задачи на отправку PDF.")

    task = pending_pdf_sends[manager_id]
    user_id = task["user_id"]
    username = task["username"]

    document = message.document
    file_name = document.file_name

    # Валидация имени файла (как у тебя)
    try:
        parts = file_name.replace(".pdf", "").split("-")
        departure_city, recipient_city, invoice_number = parts
    except Exception:
        return await message.answer("❗ Неверное имя файла. Ожидается формат: departure-recipient-invoice.pdf")

    # Тут можно сделать запросы в API, как у тебя
    async with httpx.AsyncClient() as client:
        try:
            response_user = await client.get(f"{settings.BASE_FASTAPI_URL}/user/telegram/{user_id}")
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
            return await message.answer(f"Ошибка при сохранении накладной: {str(e)}")

    # Отправляем клиенту
    await message.bot.send_document(
        chat_id=user_id,
        document=document.file_id,
        caption="📄 Ваша накладная готова!"
    )

    # Подтверждаем менеджеру
    await message.answer(f"✅ Накладная успешно отправлена пользователю @{username}")

    # Убираем задачу из ожиданий
    del pending_pdf_sends[manager_id]