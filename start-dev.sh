#!/usr/bin/env bash
set -eux
docker-compose build
docker-compose up -d azurite
docker-compose logs -f
