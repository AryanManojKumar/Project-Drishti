@echo off
echo 🐳 Building and testing Drishti Guard with Docker...

echo 📦 Stopping any running containers...
docker-compose down

echo 🏗️ Building containers...
docker-compose build

echo 🚀 Starting containers...
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 30

echo 🧪 Testing endpoints...
curl -f http://localhost:8000/api/health
curl -f http://localhost:3000

echo ✅ Drishti Guard is running!
echo 🌐 Frontend: http://localhost:3000
echo 🔗 Backend: http://localhost:8000
echo 📊 Volunteer Dashboard: http://localhost:3000/volunteer

echo 📊 Docker container status:
docker-compose ps

pause
