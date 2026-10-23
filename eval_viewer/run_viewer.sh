#!/usr/bin/env bash
set -e

SCRIPT_PATH="$(realpath "${BASH_SOURCE[0]}")"
APP_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
APP_PATH="$APP_DIR/app.py"

# Detect streamlit binary portably
if command -v streamlit >/dev/null 2>&1; then
    STREAMLIT_CMD="streamlit"
elif python -m streamlit --help >/dev/null 2>&1; then
    STREAMLIT_CMD="python -m streamlit"
elif python3 -m streamlit --help >/dev/null 2>&1; then
    STREAMLIT_CMD="python3 -m streamlit"
elif [ -n "$CONDA_PREFIX" ] && [ -f "$CONDA_PREFIX/bin/streamlit" ]; then
    STREAMLIT_CMD="$CONDA_PREFIX/bin/streamlit"
elif [ -f "$HOME/miniconda3/envs/lerobot/bin/streamlit" ]; then
    STREAMLIT_CMD="$HOME/miniconda3/envs/lerobot/bin/streamlit"
elif [ -f "$HOME/miniforge3/envs/lerobot/bin/streamlit" ]; then
    STREAMLIT_CMD="$HOME/miniforge3/envs/lerobot/bin/streamlit"
else
    echo "[Error] streamlit 실행 파일을 찾을 수 없습니다. (pip install streamlit 필요)"
    exit 1
fi

PORT="${PORT:-8501}"

echo "=================================================="
echo "Starting LeRobot LIBERO Evaluation Viewer..."
echo "App Path: $APP_PATH"
echo "URL: http://localhost:$PORT"
echo "=================================================="

$STREAMLIT_CMD run "$APP_PATH" \
    --server.port "$PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
