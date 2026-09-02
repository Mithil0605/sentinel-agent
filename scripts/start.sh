#!/usr/bin/env bash
# Start the Sentinel Agent backend. Usage: ./scripts/start.sh
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR/backend"
source "$DIR/.venv/bin/activate" 2>/dev/null || true
mkdir -p "$DIR/logs"
LOG="$DIR/logs/sentinel.log"
nohup python run.py > "$LOG" 2>&1 &
echo "Sentinel Agent started (pid $!). Log: $LOG"
