#!/bin/sh
set -e
cd /opt/osint-engine
declared=$(grep -m1 '^API_DOMAIN=' .env | cut -d= -f2-)
if [ "$declared" != "$EXPECTED_API_DOMAIN" ]; then
  echo "::error::vars.API_DOMAIN is '${EXPECTED_API_DOMAIN}' but /opt/osint-engine/.env declares '${declared}'; the health check would probe a domain Caddy does not serve"
  exit 1
fi
