from aiogram import Router

from bot.handlers.invoice.edit_invoice import router as ei_router
from bot.handlers.invoice.confirmation import router as confirm_router
from bot.handlers.invoice.contract_number import router as cn_router 
from bot.handlers.invoice.departure_address import router as da_router
from bot.handlers.invoice.departure_city import router as dc_router
from bot.handlers.invoice.insurance_amount import router as ia_router
from bot.handlers.invoice.recipient_address import router as ra_router
from bot.handlers.invoice.recipient_city import router as rc_router
from bot.handlers.invoice.recipient_phone import router as cp_router
from bot.handlers.invoice.callbacks import router as cb_router



router = Router()

router.include_routers(
    confirm_router,
    cn_router,
    da_router,
    dc_router,
    ia_router,
    ra_router,
    rc_router,
    cp_router,
    cb_router,
    ei_router
)