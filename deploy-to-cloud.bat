@echo off
echo 🚀 Drishti Guard - Google Cloud Deployment Setup
echo ===============================================

echo.
echo Before deploying, you need to:
echo 1. Install Google Cloud CLI: https://cloud.google.com/sdk/docs/install
echo 2. Create a Google Cloud Project
echo 3. Get a Gemini API key from Google AI Studio

echo.
set /p PROJECT_ID=Enter your Google Cloud Project ID: 
set /p GEMINI_KEY=Enter your Gemini API key: 

echo.
echo 📋 Project ID: %PROJECT_ID%
echo 🔑 API Key: %GEMINI_KEY:~0,10%...

echo.
set /p CONFIRM=Deploy to Google Cloud? (y/n): 
if /i "%CONFIRM%" neq "y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo 🚀 Starting deployment...
powershell -ExecutionPolicy Bypass -File "deploy-gcp.ps1" -ProjectId "%PROJECT_ID%" -GeminiApiKey "%GEMINI_KEY%"

pause
