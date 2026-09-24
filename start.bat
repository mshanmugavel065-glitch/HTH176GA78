@echo off
echo =======================================================================
echo              RESQ-AI Disaster Response Coordinator
echo =======================================================================
echo.
echo Starting Backend FastAPI Server on http://localhost:8008 ...
start "RESQ-AI Backend" cmd /k "cd /d %~dp0backend && python main.py"

echo Starting Frontend Vite Dev Server on http://localhost:3000 ...
start "RESQ-AI Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo =======================================================================
echo Both Backend & Frontend servers are launching!
echo Frontend URL: http://localhost:3000
echo Backend API : http://localhost:8008/docs
echo =======================================================================
echo.
pause
