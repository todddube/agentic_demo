@echo off
title CarMax Store Demo
color 0A

echo.
echo ===============================================
echo            🚗 CARMAX STORE DEMO 🚗
echo ===============================================
echo.
echo Starting CarMax store team simulation...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python first.
    pause
    exit /b 1
)

REM Check if required packages are installed
python -c "import pygame, requests" >nul 2>&1
if errorlevel 1 (
    echo 📦 Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install packages!
        pause
        exit /b 1
    )
)

echo ✅ Dependencies ready!
echo.
echo 🎮 Launching CarMax Store Demo...
echo    (A pygame window will open with the store interface)
echo.

REM Run the demo
python simple_demo.py

echo.
echo 👋 Thanks for trying the CarMax Store Demo!
pause
