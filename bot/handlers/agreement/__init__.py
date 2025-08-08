from aiogram import Router

from bot.handlers.agreement.process_phone import router as pp_router
from bot.handlers.agreement.process_tin import router as pt_router


router = Router()


router.include_routers(
    pp_router,
    pt_router,
)