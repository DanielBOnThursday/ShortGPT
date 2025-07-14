#!/bin/bash
# Kill process on port 31415
PORT=31415
PID=$(lsof -ti:$PORT)

if [ -n "$PID" ]; then
    echo "Killing process $PID on port $PORT"
    kill -9 $PID
    echo "Process killed successfully"
else
    echo "No process found on port $PORT"
fi