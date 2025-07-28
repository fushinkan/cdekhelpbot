FROM python:3.12-slim

RUN pip install poetry

WORKDIR /project

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main --no-root

COPY bot ./bot
COPY app ./app

ENV PYTHONPATH=/project

CMD ["python", "-m", "bot.bot"]