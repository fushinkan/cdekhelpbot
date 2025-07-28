from aiogram import Router

from bot.handlers.authorization.admin_auth import router as admin_router
from bot.handlers.callbacks.process_phone_callback import router as pphone_router
from bot.handlers.authorization.customer_auth import router as customer_router
from bot.handlers.authorization.process_role import router as role_router
from bot.handlers.authorization.first_login import router as first_login_router

router = Router()

router.include_routers(
    role_router,
    customer_router,
    admin_router,
    pphone_router,
    first_login_router
)