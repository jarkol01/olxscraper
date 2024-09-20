# syntax=docker/dockerfile:1

FROM python:3.11.9-alpine3.20 AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=olxscraper.settings.prod

WORKDIR /app


RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements,target=requirements \
    python -m pip install --no-cache-dir -r requirements/prod.txt

COPY .. .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "olxscraper.wsgi:application", "--bind", "0.0.0.0:8000"]
