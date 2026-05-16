@echo off
title Drillingo - Stop
color 0C

echo.
echo  Stopping Drillingo...
echo.

:: Stop backend and frontend windows
taskkill /FI "WINDOWTITLE eq Drillingo Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq Drillingo Frontend*" /F >nul 2>&1

:: Stop Docker containers
cd /d "%~dp0"
docker-compose stop db >nul 2>&1

echo  All services stopped.
echo.
timeout /t 2 /nobreak >nul
