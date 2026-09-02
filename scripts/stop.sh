#!/usr/bin/env bash
# Stop the Sentinel Agent backend. Usage: ./scripts/stop.sh
set -e
PORT="${PORT:-8000}"
if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" >/dev/null 2>&1 || true
  echo "Stopped backend on port $PORT (via fuser)."
else
  echo "fuser not available; please stop the server manually."
fi
