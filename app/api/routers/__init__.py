from fastapi import APIRouter

from app.api.routers.auth import router as auth_router
from app.api.routers.get_user import router as get_user_router
from app.api.routers.invoice import router as invoice_router


router = APIRouter()
router.include_router(auth_router)
router.include_router(get_user_router)
router.include_router(invoice_router)