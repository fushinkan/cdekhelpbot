from aiogram import Router

from bot.handlers.authorization.customer_auth.first_login import router as client_first_login_router
from bot.handlers.authorization.customer_auth.set_password import router as client_set_password_router 
from bot.handlers.authorization.customer_auth.confirm_password import router as client_confirm_password_router
from bot.handlers.authorization.customer_auth.accept_enter import router as client_accept_router

router = Router()

router.include_routers(
    client_first_login_router,
    client_set_password_router,
    client_confirm_password_router,
    client_accept_router
)