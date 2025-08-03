from aiogram import Router

from bot.handlers.customer.city import router as city_router
from bot.handlers.customer.contract_number import router as contract_number_router
from bot.handlers.customer.contractor import router as contractor_router
from bot.handlers.customer.number import router as number_router


router = Router()


router.include_routers(
    city_router,
    contract_number_router,
    contractor_router,
    number_router
)