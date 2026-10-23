#!/bin/sh
set -e
cd /opt/osint-engine
git fetch --quiet origin
git reset --hard "$SHA"
export IMAGE_TAG="$SHA"
docker compose -f docker-compose.yml -f compose.prod.yml pull
docker compose -f docker-compose.yml -f compose.prod.yml up -d
