ARG PYTHON_VERSION
FROM ghcr.io/astral-sh/uv:0.9-python${PYTHON_VERSION:-3.13}-alpine

WORKDIR /app

COPY . /app

RUN uv sync --locked
