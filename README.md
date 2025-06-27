# Telegram-бот для менеджеров + REST API


Telegram-бот , разработанный для помощи менеджерам по продажам СДЭК.
Предоставляет REST API и бота с ролевой авторизацией (`user` или `admin`).
Включает функции создания накладных, договоров, связи с поддержкой, получения информации о доп.услугах, тарифах и мерче.


---


## Стек технологий

- 🐍 Python 3.12
- 🚀 FastAPI (асинхронный REST API)
- 🤖 Aiogram (Telegram Bot Framework)
- 🧱 SQLAlchemy 2.0 (async)
- 🔐 JWT (авторизация, хранение refresh-токенов)
- 🐘 PostgreSQL
- 🔄 Alembic (миграции)
- ⚡ Redis (сессии, состояния бота)
- 🐳 Docker + Docker Compose

---



