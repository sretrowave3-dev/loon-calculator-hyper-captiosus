@echo off
setlocal
cd /d "%~dp0"
title Smart AI Calculator ^& Calculus Assistant
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8

:: 1. Try Python 3.15 specifically via py launcher
py -3.15 smart_calculator.py %* 2>nul
if %errorlevel% equ 0 goto :done

:: 2. Try default py launcher
py smart_calculator.py %* 2>nul
if %errorlevel% equ 0 goto :done

:: 3. Try python executable in PATH
python smart_calculator.py %* 2>nul
if %errorlevel% equ 0 goto :done

:: 4. Direct fallback to Python 3.15 program directory
if exist "%LocalAppData%\Programs\Python\Python315\python.exe" (
    "%LocalAppData%\Programs\Python\Python315\python.exe" smart_calculator.py %*
    goto :done
)

echo.
echo ================================================================
echo  [ERROR] Could not start Smart Calculator with Python.
echo  Please ensure Python 3.15 or the Windows py launcher is installed.
echo ================================================================
pause

:done
