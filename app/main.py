import uvicorn
from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from app.api.routers.get_user import router as get_user_router
from app.api.routers.invoice import router as invoice_router
from app.api.routers.customers import router as customers_router
from app.api.routers.tariffs import router as  tariffs_router
from app.api.routers.extra_services import router as services_router
from app.api.routers.history import router as history_router
from app.api.routers.jwt_storage import router as jwt_router

app = FastAPI(title="Telegram Bot API")
app.include_router(auth_router)
app.include_router(get_user_router)
app.include_router(invoice_router)
app.include_router(customers_router)
app.include_router(tariffs_router)
app.include_router(services_router)
app.include_router(history_router)
app.include_router(jwt_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app")