FROM python:3.13-slim

RUN pip install uv

WORKDIR /app

COPY pyproject.toml .python-version ./
RUN uv sync --frozen
RUN uvx playwright install
RUN uvx playwright install-deps

COPY app/ ./app/
