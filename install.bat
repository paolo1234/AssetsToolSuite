@echo off
setlocal enabledelayedexpansion

echo ################################################
echo #      OmniForge Asset Suite - Installer       #
echo ################################################
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python non trovato. Installa Python 3.10+ e riprova.
    pause
    exit /b 1
)

:: Check for Node
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js non trovato. Installa Node.js 18+ e riprova.
    pause
    exit /b 1
)

echo [1/3] Installazione dipendenze Backend...
cd omniforge\backend
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Errore durante l'installazione delle dipendenze Python.
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo.
echo [2/3] Installazione dipendenze Frontend...
cd omniforge\frontend
call npm install
if %errorlevel% neq 0 (
    echo [ERROR] Errore durante l'installazione delle dipendenze Node.
    cd ..\..
    pause
    exit /b 1
)
cd ..\..

echo.
echo [3/3] Configurazione finale...
if not exist "omniforge_data" mkdir "omniforge_data"

echo.
echo ################################################
echo #      INSTALLAZIONE COMPLETATA CON SUCCESSO   #
echo ################################################
echo.
echo Ora puoi avviare la suite con: start.bat
echo.
pause
