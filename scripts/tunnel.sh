#!/usr/bin/env bash
# Start (or restart) a public tunnel to the running Sentinel Agent.
# Exposes localhost:8000 to the internet via localhost.run (no account needed).
# The returned URL is TEMPORARY: it dies if this machine reboots or the SSH
# process stops. Restart with this script and re-read the log for the new URL.
#
# Usage: ./scripts/tunnel.sh
set -e

PORT="${PORT:-8000}"

# Stop any existing tunnel.
if command -v fuser >/dev/null 2>&1; then
  pkill -f "localhost.run" >/dev/null 2>&1 || true
fi
sleep 1

echo "Starting public tunnel for http://127.0.0.1:${PORT} ..."
(ssh -o StrictHostKeyChecking=no -o ServerAliveInterval=30 \
     -R 80:localhost:${PORT} nokey@localhost.run > /tmp/tunnel.log 2>&1 &)

# Wait for the public URL to appear.
URL=""
for _ in $(seq 1 15); do
  URL=$(grep -oE "https://[a-z0-9]+\.lhr\.life" /tmp/tunnel.log | head -1 || true)
  [ -n "$URL" ] && break
  sleep 2
done

if [ -n "$URL" ]; then
  echo ""
  echo "========================================================"
  echo "  PUBLIC URL:  $URL"
  echo "========================================================"
  echo "  (temporary - see scripts/tunnel.sh notes)"
else
  echo "Could not determine public URL yet. Check:"
  echo "  cat /tmp/tunnel.log"
fi
