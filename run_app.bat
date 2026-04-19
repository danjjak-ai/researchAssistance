@echo off
setlocal
cd /d "%~dp0"

echo [Research Assistant] Starting application...

:: Check for uv
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] uv is not installed. Please install it first.
    pause
    exit /b 1
)

:: Sync dependencies if .venv doesn't exist
if not exist ".venv" (
    echo [INFO] Creating virtual environment and installing dependencies...
    uv sync
)

:: Run the Gradio UI
echo [INFO] UI will be available at http://localhost:7860
uv run python -m src.ui.gradio_app

pause
