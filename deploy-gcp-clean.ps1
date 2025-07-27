# PowerShell deployment script for Google Cloud Run
param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    
    [Parameter(Mandatory=$true)]
    [string]$GeminiApiKey,
    
    [string]$Region = "us-central1"
)

Write-Host "Deploying Drishti Guard to Google Cloud Run..." -ForegroundColor Green

# Check if gcloud is installed
try {
    $gcloudVersion = gcloud version 2>&1
    Write-Host "Google Cloud CLI found" -ForegroundColor Green
} catch {
    Write-Host "Google Cloud CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host "Project ID: $ProjectId" -ForegroundColor Cyan
Write-Host "Region: $Region" -ForegroundColor Cyan

# Set project
Write-Host "Setting up Google Cloud project..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# Enable APIs
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
$apis = @(
    "cloudbuild.googleapis.com",
    "run.googleapis.com", 
    "containerregistry.googleapis.com",
    "secretmanager.googleapis.com"
)

foreach ($api in $apis) {
    Write-Host "  Enabling $api..." -ForegroundColor Gray
    gcloud services enable $api
}

# Create secret
Write-Host "Creating secret for Gemini API key..." -ForegroundColor Yellow
try {
    $GeminiApiKey | gcloud secrets create gemini-api-key --data-file=-
    Write-Host "Secret created successfully" -ForegroundColor Green
} catch {
    Write-Host "Updating existing secret..." -ForegroundColor Yellow
    $GeminiApiKey | gcloud secrets versions add gemini-api-key --data-file=-
}

# Deploy backend
Write-Host "Building and deploying backend..." -ForegroundColor Yellow
gcloud builds submit --config cloudbuild-backend.yaml .

if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend deployment failed!" -ForegroundColor Red
    exit 1
}

# Get backend URL
Write-Host "Getting backend URL..." -ForegroundColor Yellow
$backendUrl = gcloud run services describe drishti-guard-backend --region $Region --format "value(status.url)"
Write-Host "Backend URL: $backendUrl" -ForegroundColor Green

# Update frontend config with backend URL
Write-Host "Updating frontend configuration..." -ForegroundColor Yellow
$frontendConfig = Get-Content "ui\cloudbuild.yaml" -Raw
$frontendConfig = $frontendConfig -replace "https://drishti-guard-backend-.*-uc\.a\.run\.app", $backendUrl
$frontendConfig | Set-Content "ui\cloudbuild.yaml"

# Deploy frontend
Write-Host "Building and deploying frontend..." -ForegroundColor Yellow
gcloud builds submit --config ui/cloudbuild.yaml ui/

if ($LASTEXITCODE -ne 0) {
    Write-Host "Frontend deployment failed!" -ForegroundColor Red
    exit 1
}

# Get frontend URL
Write-Host "Getting frontend URL..." -ForegroundColor Yellow
$frontendUrl = gcloud run services describe drishti-guard-frontend --region $Region --format "value(status.url)"

# Display results
Write-Host ""
Write-Host "Deployment completed successfully!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan
Write-Host "Frontend URL: $frontendUrl" -ForegroundColor Green
Write-Host "Backend API: $backendUrl" -ForegroundColor Green  
Write-Host "Volunteer Dashboard: $frontendUrl/volunteer" -ForegroundColor Green
Write-Host "API Documentation: $backendUrl/docs" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Cyan

# Test deployment
Write-Host "Testing deployment..." -ForegroundColor Yellow

try {
    $backendTest = Invoke-WebRequest -Uri "$backendUrl/api/health" -TimeoutSec 30
    Write-Host "Backend health check passed!" -ForegroundColor Green
} catch {
    Write-Host "Backend health check failed: $_" -ForegroundColor Red
}

try {
    $frontendTest = Invoke-WebRequest -Uri $frontendUrl -TimeoutSec 30
    Write-Host "Frontend health check passed!" -ForegroundColor Green
} catch {
    Write-Host "Frontend health check failed: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Access your application at: $frontendUrl" -ForegroundColor White
Write-Host "2. Configure custom domain if needed" -ForegroundColor White
Write-Host "3. Set up monitoring and alerts" -ForegroundColor White
Write-Host "4. Review Cloud Run logs for any issues" -ForegroundColor White

Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "View logs: gcloud run services logs read drishti-guard-frontend --region $Region" -ForegroundColor Gray
Write-Host "View logs: gcloud run services logs read drishti-guard-backend --region $Region" -ForegroundColor Gray
Write-Host "Delete services: gcloud run services delete drishti-guard-frontend --region $Region" -ForegroundColor Gray
