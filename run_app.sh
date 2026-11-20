#!/bin/bash
set -e

echo "====================================================================="
echo "   STARTING CHANAKYA RESEARCH COMMONS (CRC) PLATFORM"
echo "   Chanakya University, Bangalore - Data Mining and Warehousing"
echo "====================================================================="

cd "$(dirname "$0")"

echo "[1/2] Starting FastAPI Backend on port 8000..."
(cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &
BACKEND_PID=$!

echo "[2/2] Starting React Frontend on port 5173..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo ""
echo "Platform running!"
echo "Backend Swagger Docs: http://127.0.0.1:8000/docs"
echo "Web UI:               http://localhost:5173"
echo "Press Ctrl+C to terminate both servers."
wait
