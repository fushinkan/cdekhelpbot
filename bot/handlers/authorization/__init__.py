from aiogram import Router

from bot.handlers.authorization.process_password import router as pp_router
from bot.handlers.authorization.process_phone import router as pphone_router
from bot.handlers.authorization.process_role import router as pr_router

router = Router()

router.include_routers(
    pp_router,
    pphone_router,
    pr_router
)