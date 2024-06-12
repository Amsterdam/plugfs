#!/usr/bin/env bash
set -eux
isort .
black .
mypy .
pytest -xsvv
