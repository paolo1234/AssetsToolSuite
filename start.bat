@echo off
echo ################################################
echo #      OmniForge Asset Suite - Launcher        #
echo ################################################
echo.

:: Avvia il Backend in una nuova finestra
echo Avvio del Backend...
start "OmniForge Backend" cmd /k "cd omniforge\backend && set PYTHONPATH=.&& python main.py"

:: Attendi qualche secondo per il backend
timeout /t 3 /nobreak >nul

:: Avvia il Frontend in una nuova finestra
echo Avvio del Frontend...
start "OmniForge Frontend" cmd /k "cd omniforge\frontend && npm run dev"

echo.
echo Suite avviata! 
echo - Backend: http://localhost:47831
echo - Frontend: http://localhost:5173
echo.
echo Chiudi le finestre dei terminali per fermare i server.
echo.
pause
