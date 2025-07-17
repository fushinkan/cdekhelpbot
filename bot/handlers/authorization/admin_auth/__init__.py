from aiogram import Router

from bot.handlers.authorization.admin_auth.first_login import router as admin_first_login_router
from bot.handlers.authorization.admin_auth.set_password import router as admin_set_password_router 
from bot.handlers.authorization.admin_auth.confirm_password import router as admin_confirm_password_router
from bot.handlers.authorization.admin_auth.accept_enter import router as admin_accept_router

router = Router()

router.include_routers(
    admin_first_login_router,
    admin_set_password_router,
    admin_confirm_password_router,
    admin_accept_router
)