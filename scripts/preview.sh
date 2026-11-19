#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
python3 build/build.py
exec python3 scripts/preview.py --port "${PORT:-8080}"
