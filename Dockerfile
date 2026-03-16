FROM python:3.13-slim

WORKDIR /app

COPY . .

RUN pip install uv
RUN uv sync
RUN uvx playwright install
RUN uvx playwright install-deps
