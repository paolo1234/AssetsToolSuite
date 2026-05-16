@echo off
echo ################################################
echo #      OmniForge Asset Suite - Launcher        #
echo ################################################
echo.

:: Imposta il percorso del backend per gli import
set PYTHONPATH=%CD%\omniforge\backend

echo [1/2] Avvio Backend in background...
start /b cmd /c "cd omniforge\backend && python main.py"

echo [2/2] Avvio Frontend...
echo.
echo La suite sara' disponibile a breve su: http://localhost:5173
echo.
echo Premi CTRL+C per fermare tutto.
echo ------------------------------------------------
echo.

cd omniforge\frontend
npm run dev
