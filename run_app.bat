@echo off
echo =====================================================================
echo    STARTING CHANAKYA RESEARCH COMMONS (CRC) PLATFORM
echo    Chanakya University, Bangalore - Data Mining and Warehousing
echo =====================================================================
echo.

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on port 8000...
start "CRC Backend (FastAPI)" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting React Frontend on port 5173...
start "CRC Frontend (Vite React)" cmd /k "cd frontend && npm run dev"

echo.
echo =====================================================================
echo Platform is launching!
echo Backend Swagger API Docs: http://127.0.0.1:8000/docs
echo Web Application UI:       http://localhost:5173
echo =====================================================================
pause
