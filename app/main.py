import uvicorn
from fastapi import FastAPI

from app.api.routers.users import router as users_router

app = FastAPI(title="Telegram Bot API")

app.include_router(users_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
