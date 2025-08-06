from aiogram import Router

from bot.handlers.callbacks.client_callbacks.extra_services import router as services_router
from bot.handlers.callbacks.client_callbacks.history import router as history_router
from bot.handlers.callbacks.client_callbacks.tariff_subraiff import router as tariff_router


router = Router()


router.include_routers(
    services_router,
    history_router,
    tariff_router
)
