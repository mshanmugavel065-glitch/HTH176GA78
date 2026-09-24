#!/bin/bash
echo "======================================================================="
echo "             RESQ-AI Disaster Response Coordinator"
echo "======================================================================="
echo ""
echo "Starting Backend FastAPI Server on http://localhost:8008 ..."
(cd backend && python main.py) &
BACKEND_PID=$!

echo "Starting Frontend Vite Dev Server on http://localhost:3000 ..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo ""
echo "Both servers are running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8008/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
