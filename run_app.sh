#!/bin/bash

# Move to the directory where the script is located
cd "$(dirname "$0")"

echo "[Research Assistant] Starting application..."

# Check for uv
if ! command -v uv &> /dev/null
then
    echo "[ERROR] uv is not installed. Please install it first."
    exit 1
fi

# Sync dependencies if .venv doesn't exist
if [ ! -d ".venv" ]; then
    echo "[INFO] Creating virtual environment and installing dependencies..."
    uv sync
fi

# Run the Gradio UI
echo "[INFO] UI will be available at http://localhost:7860"
uv run python -m src.ui.gradio_app
