
echo.
echo Building and Watching the frontend
echo.
cd frontend
call npm run watch
if "%errorlevel%" neq "0" (
    echo Failed to build frontend
    exit /B %errorlevel%