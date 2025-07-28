FROM python:3.12-slim

RUN pip install poetry

WORKDIR /project

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --only main --no-root

COPY app ./app
COPY bot ./bot

ENV PYTHONPATH=/project

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]