from aiogram import Router

from bot.handlers.callbacks.back_to_callbacks import router as back_to_callbacks_router
from bot.handlers.callbacks.invoice_callbacks import router as invoice_callback_router
from bot.handlers.callbacks.agreement_callbacks import router as agreement_callbacks_router
from bot.handlers.callbacks.edit_field_callbacks import router as edit_field_router
from bot.handlers.callbacks.manager_callbacks import router as send_router 
from bot.handlers.callbacks.add_customer_callbacks import router as add_customer_router
from bot.handlers.callbacks.client_callbacks import router as client_router


router = Router()


router.include_routers(
    back_to_callbacks_router,
    invoice_callback_router,
    agreement_callbacks_router,
    edit_field_router,
    send_router,
    add_customer_router,
    client_router
)