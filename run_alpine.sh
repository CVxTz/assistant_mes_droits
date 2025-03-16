#!/usr/bin/env bash

if [ "$1" = "prod" ]; then
    echo "Starting Uvicorn server in production mode..."
    # we also use a single worker in production mode so socket.io connections are always handled by the same worker
    uvicorn assistant_mes_droits.alpine_app.main:app --workers 1 --log-level info --port "8080" --host "0.0.0.0"
else
    echo "Starting Uvicorn server in development mode..."
    uvicorn assistant_mes_droits.alpine_app.main:app --workers 1 --reload --log-level debug --port "8080" --host "0.0.0.0"
fi