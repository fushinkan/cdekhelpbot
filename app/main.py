import uvicorn
from fastapi import FastAPI

from app.api.routers import router as main_router

app = FastAPI(title="Telegram Bot API")
app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True)
