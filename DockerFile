FROM python:3.13-slim

WORKDIR /app

ENV POETRY_HOME="/opt/poetry"
ENV POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"
        
RUN pip install poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-ansi

COPY . .
