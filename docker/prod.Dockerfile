# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.9
FROM python:${PYTHON_VERSION} AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=olxscraper.settings.prod

WORKDIR /app

RUN python -m pip install --upgrade pip

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=bind,source=requirements,target=requirements \
    python -m pip install --no-cache-dir -r requirements/prod.txt

COPY .. .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "olxscraper.wsgi:application", "--bind", "0.0.0.0:8000"]
