FROM python:3.12-slim

WORKDIR /project

# Устанавливаем poetry и зависимости
COPY pyproject.toml poetry.lock ./
RUN pip install poetry \
 && poetry config virtualenvs.create false \
 && poetry install --only main --no-root

# Копируем саму папку с alembic и app
COPY migrations ./migrations
COPY app ./app

# Рабочая директория должна совпадать с `alembic.ini` или `env.py`
WORKDIR /project

CMD ["alembic", "upgrade", "head"]
