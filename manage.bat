@echo off
REM CommuteOS Management Script for Windows
REM Quick commands to manage the CommuteOS backend

:menu
echo.
echo ========================================
echo CommuteOS Management Script
echo ========================================
echo.
echo 1. Start all services
echo 2. Stop all services
echo 3. View logs (all)
echo 4. View API Gateway logs
echo 5. View Routing Service logs
echo 6. Check service status
echo 7. Rebuild and restart
echo 8. Run tests
echo 9. Setup verification
echo 0. Exit
echo.
set /p choice="Enter your choice: "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto logs_all
if "%choice%"=="4" goto logs_api
if "%choice%"=="5" goto logs_routing
if "%choice%"=="6" goto status
if "%choice%"=="7" goto rebuild
if "%choice%"=="8" goto test
if "%choice%"=="9" goto setup
if "%choice%"=="0" goto end
goto menu

:start
echo Starting all services...
docker-compose up -d
echo.
echo Services started! Access the API at http://localhost:8000
timeout /t 3 >nul
goto menu

:stop
echo Stopping all services...
docker-compose down
echo Services stopped!
timeout /t 2 >nul
goto menu

:logs_all
echo Showing logs for all services (Ctrl+C to exit)...
docker-compose logs -f
goto menu

:logs_api
echo Showing API Gateway logs (Ctrl+C to exit)...
docker-compose logs -f api
goto menu

:logs_routing
echo Showing Routing Service logs (Ctrl+C to exit)...
docker-compose logs -f routing_service
goto menu

:status
echo Checking service status...
docker-compose ps
echo.
pause
goto menu

:rebuild
echo Rebuilding and restarting all services...
docker-compose down
docker-compose build --no-cache
docker-compose up -d
echo Rebuild complete!
timeout /t 3 >nul
goto menu

:test
echo Running tests...
pytest commuteos/tests/
pause
goto menu

:setup
echo Running setup verification...
python setup.py
pause
goto menu

:end
echo Goodbye!
exit
