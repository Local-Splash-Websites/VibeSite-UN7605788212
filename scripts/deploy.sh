#!/bin/sh
# Build the static site. Coolify deploys from the Dockerfile on merge to main.
# This script does not upload secrets and does not call a leads API.
set -eu
cd "$(dirname "$0")/.."
python3 build/build.py

if [ -n "${DEPLOY_TARGET:-}" ]; then
  echo "Syncing public/ to ${DEPLOY_TARGET}"
  rsync -a --delete public/ "${DEPLOY_TARGET}/"
else
  echo "Build complete in public/."
  echo "Set DEPLOY_TARGET to rsync the files, or merge to main so Coolify builds the Dockerfile."
fi
