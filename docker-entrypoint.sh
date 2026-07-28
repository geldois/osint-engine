#!/bin/sh
set -e

osint-engine wait-db
osint-engine migrate up
exec osint-engine serve
