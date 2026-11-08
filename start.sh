#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

echo "================================================"
echo "  Agnes Video Generator"
echo "================================================"

if ! command -v python3 >/dev/null 2>&1; then
  echo "ERROR: python3 is required."
  exit 1
fi

python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" || {
  echo "ERROR: Python 3.10 or newer is required."
  exit 1
}

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ERROR: ffmpeg is required."
  exit 1
fi

if command -v lsof >/dev/null 2>&1; then
  PID="$(lsof -ti:8765 2>/dev/null || true)"
  if [ -n "$PID" ]; then
    echo "ERROR: Port 8765 is already in use (PID $PID)."
    exit 1
  fi
fi

VENV_DIR=".venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"

if [ ! -x "$VENV_PYTHON" ]; then
  echo "[1/3] Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "[2/3] Installing requirements..."
"$VENV_PIP" install -q -r requirements.txt

echo "[3/3] Starting server..."
echo "Open the forwarded port 8765 in Codespaces to use the app."
exec "$VENV_PYTHON" server.py
