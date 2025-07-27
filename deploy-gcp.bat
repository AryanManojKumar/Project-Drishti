@echo off
echo 🚀 Deploying Drishti Guard to Google Cloud Run...

REM Configuration - UPDATE THESE VALUES
set PROJECT_ID=your-gcp-project-id-here
set REGION=us-central1
set GEMINI_API_KEY=your-gemini-api-key-here

echo 📋 Using Project ID: %PROJECT_ID%
echo 📍 Region: %REGION%

REM Check if gcloud is installed
gcloud version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Google Cloud CLI not found. Please install it first:
    echo https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

echo 🔧 Setting up Google Cloud project...
gcloud config set project %PROJECT_ID%

echo 🔐 Enabling required APIs...
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

echo 🔑 Creating secret for Gemini API key...
echo %GEMINI_API_KEY% | gcloud secrets create gemini-api-key --data-file=- || (
    echo Updating existing secret...
    echo %GEMINI_API_KEY% | gcloud secrets versions add gemini-api-key --data-file=-
)

echo 🏗️ Building and deploying backend...
gcloud builds submit --config cloudbuild-backend.yaml .

echo ⏳ Getting backend URL...
for /f "tokens=*" %%i in ('gcloud run services describe drishti-guard-backend --region %REGION% --format "value(status.url)"') do set BACKEND_URL=%%i
echo 🔗 Backend URL: %BACKEND_URL%

echo 🏗️ Building and deploying frontend...
REM Update frontend environment with backend URL
powershell -Command "(Get-Content ui\cloudbuild.yaml) -replace 'https://drishti-guard-backend-.*-uc\.a\.run\.app', '%BACKEND_URL%' | Set-Content ui\cloudbuild.yaml"

gcloud builds submit --config ui/cloudbuild.yaml ui/

echo ⏳ Getting frontend URL...
for /f "tokens=*" %%i in ('gcloud run services describe drishti-guard-frontend --region %REGION% --format "value(status.url)"') do set FRONTEND_URL=%%i

echo ✅ Deployment completed successfully!
echo ===========================================
echo 🌐 Frontend URL: %FRONTEND_URL%
echo 🔗 Backend API: %BACKEND_URL%
echo 📊 Volunteer Dashboard: %FRONTEND_URL%/volunteer
echo 📚 API Documentation: %BACKEND_URL%/docs
echo ===========================================

echo 🧪 Testing deployment...
curl -f %BACKEND_URL%/api/health
if %errorlevel% equ 0 (
    echo ✅ Backend health check passed!
) else (
    echo ⚠️ Backend health check failed
)

curl -f %FRONTEND_URL%
if %errorlevel% equ 0 (
    echo ✅ Frontend health check passed!
) else (
    echo ⚠️ Frontend health check failed
)

echo 📝 Next steps:
echo 1. Access your application at: %FRONTEND_URL%
echo 2. Configure custom domain if needed
echo 3. Set up monitoring and alerts
echo 4. Review Cloud Run logs for any issues

pause
