@echo off
chcp 65001 >nul
echo ========================================
echo   Démarrage Backend Flask + Frontend React
echo ========================================
echo.

echo [1/2] Démarrage du backend Flask (port 5000)...
start "Backend Flask" cmd /k "python app.py"

timeout /t 3 /nobreak >nul

echo [2/2] Démarrage du frontend React (port 5173)...
start "Frontend React" cmd /k "cd frontend && npm run dev"

timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo   ✓ Serveurs démarrés !
echo ========================================
echo.
echo   Backend Flask:  http://localhost:5000
echo   Frontend React: http://localhost:5173
echo.
echo   Ouvrez http://localhost:5173 dans votre navigateur
echo.
echo   Appuyez sur une touche pour fermer cette fenêtre...
pause >nul
