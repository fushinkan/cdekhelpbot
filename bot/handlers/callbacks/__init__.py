from aiogram import Router

from bot.handlers.callbacks.back_to_callbacks import router as back_to_callbacks_router
from bot.handlers.callbacks.invoice_callbacks import router as invoice_callback_router

router = Router()

router.include_routers(
    back_to_callbacks_router,
    invoice_callback_router
)