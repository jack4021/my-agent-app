FROM python:3.13-slim

WORKDIR /usr/src

COPY . .

RUN pip install uv
RUN uv sync --frozen
RUN uvx playwright install
RUN uvx playwright install-deps
