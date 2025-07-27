@echo off
echo 🚀 Starting Drishti Guard Complete System
echo ==========================================

echo.
echo 📂 Checking directories...
if not exist "bhai ka kaam\prediction" (
    echo ❌ Backend directory not found!
    echo Please run this script from the nf2 folder
    pause
    exit /b 1
)

if not exist "ui" (
    echo ❌ UI directory not found!
    echo Please run this script from the nf2 folder
    pause
    exit /b 1
)

echo ✅ Directories found

echo.
echo 🐍 Starting Backend (FastAPI)...
echo Starting in new window...
start "Drishti Backend" cmd /k "cd /d bhai ka kaam\prediction && python -m uvicorn fastapi_bridge:app --reload --port=8000"

echo.
echo ⏱️  Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo 🌐 Starting Frontend (Next.js)...
echo Starting in new window...
start "Drishti Frontend" cmd /k "cd /d ui && npm run dev"

echo.
echo ⏱️  Waiting 10 seconds for services to initialize...
timeout /t 10 /nobreak >nul

echo.
echo 🧪 Testing integration...
python test_integration.py endpoints

echo.
echo 🎯 DRISHTI GUARD SYSTEM STARTED!
echo ================================
echo.
echo 📡 Backend API: http://localhost:8000
echo    - Health: http://localhost:8000/api/health
echo    - Docs: http://localhost:8000/docs
echo.
echo 🌐 Frontend: http://localhost:3000
echo    - Volunteer Dashboard: http://localhost:3000/volunteer
echo.
echo 🔧 To test the integration:
echo    1. Open http://localhost:3000/volunteer
echo    2. Click "Start Analysis" button
echo    3. Wait for live CNS data to load
echo.
echo 📊 The system will:
echo    - Analyze your IP camera feed (192.168.0.119:8080)
echo    - Extract crowd insights and anomaly alerts
echo    - Display real-time data in the volunteer dashboard
echo.
echo Press any key to run full integration test...
pause >nul

echo.
echo 🧪 Running full integration test...
python test_integration.py

echo.
echo ✅ Integration test complete!
echo Your Drishti Guard system is ready to use.
echo.
pause
