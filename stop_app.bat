@echo off
setlocal

echo [Research Assistant] Stopping application on port 7860...

for /f "tokens=5" %%a in ('netstat -aon ^| findstr :7860 ^| findstr LISTENING') do (
    echo [INFO] Killing process with PID: %%a
    taskkill /pid %%a /f
)

if %errorlevel% neq 0 (
    echo [INFO] No application found running on port 7860.
) else (
    echo [SUCCESS] Application stopped.
)

pause
