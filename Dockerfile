# syntax=docker/dockerfile:1

FROM python:3.11.9-alpine3.20 AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=olxscraper.settings.dev

WORKDIR /app


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements,target=requirements \
    python -m pip install --no-cache-dir -r requirements/dev.txt

COPY .. .

RUN chmod +x ./docker/entrypoints/server-entrypoint.sh ./docker/entrypoints/worker-entrypoint.sh ./docker/entrypoints/beat-entrypoint.sh
