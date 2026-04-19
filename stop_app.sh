#!/bin/bash

echo "[Research Assistant] Stopping application on port 7860..."

PID=$(lsof -t -i:7860)

if [ -z "$PID" ]; then
    echo "[INFO] No application found running on port 7860."
else
    echo "[INFO] Killing process with PID: $PID"
    kill -9 $PID
    echo "[SUCCESS] Application stopped."
fi
