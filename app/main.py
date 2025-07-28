import uvicorn
from fastapi import FastAPI

from app.api.routers.get_user import router as get_user_router
from app.api.routers.auth import router as auth_router

app = FastAPI(title="Telegram Bot API")
app.include_router(auth_router)
app.include_router(get_user_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
