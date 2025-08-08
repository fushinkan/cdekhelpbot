from aiogram import Router

from bot.handlers.agreement import router as agreement_router
from bot.handlers.authorization import router as auth_router
from bot.handlers.callbacks import router as callbacks_router
from bot.handlers.command_start import router as cmd_start_router
from bot.handlers.invoice import router as invoice_router
from bot.handlers.customer import router as customer_router
from bot.handlers.merch.tin import router as m_router


router = Router()


router.include_routers(
    cmd_start_router,
    agreement_router,
    auth_router,
    callbacks_router,
    invoice_router,
    customer_router,
    m_router
)