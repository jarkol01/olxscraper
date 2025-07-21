FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

WORKDIR /app

COPY . .

RUN python -m venv --copies .venv

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --dev

ENV PATH="/app/.venv/bin:$PATH"
