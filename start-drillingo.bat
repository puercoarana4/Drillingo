@echo off
title Drillingo Launcher
color 0C

echo.
echo  ██████╗ ██████╗ ██╗██╗     ██╗     ██╗███╗   ██╗ ██████╗  ██████╗
echo  ██╔══██╗██╔══██╗██║██║     ██║     ██║████╗  ██║██╔════╝ ██╔═══██╗
echo  ██║  ██║██████╔╝██║██║     ██║     ██║██╔██╗ ██║██║  ███╗██║   ██║
echo  ██║  ██║██╔══██╗██║██║     ██║     ██║██║╚██╗██║██║   ██║██║   ██║
echo  ██████╔╝██║  ██║██║███████╗███████╗██║██║ ╚████║╚██████╔╝╚██████╔╝
echo  ╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝
echo.
echo  Starting Drillingo...
echo.

:: Check if Docker Desktop is running
echo [1/4] Checking Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo  Docker Desktop is not running. Starting it...
    start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    echo  Waiting 20 seconds for Docker to start...
    timeout /t 20 /nobreak >nul
)
echo  Docker OK

:: Start PostgreSQL container
echo [2/4] Starting database...
cd /d "%~dp0"
docker-compose up -d db >nul 2>&1
echo  Database OK

:: Start Backend in new window
echo [3/4] Starting backend...
start "Drillingo Backend" cmd /k "cd /d %~dp0backend && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul
echo  Backend starting...

:: Start Frontend in new window
echo [4/4] Starting frontend...
start "Drillingo Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"
timeout /t 5 /nobreak >nul
echo  Frontend starting...

echo.
echo  ============================================
echo   Drillingo is starting up!
echo   
echo   Backend API:  http://localhost:8000/docs
echo   App:          http://localhost:3000
echo  ============================================
echo.
echo  Opening browser in 8 seconds...
timeout /t 8 /nobreak >nul

start "" "http://localhost:3000"

echo.
echo  Press any key to close this launcher window.
echo  (Backend and Frontend will keep running in their own windows)
pause >nul
