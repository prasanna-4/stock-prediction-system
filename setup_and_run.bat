@echo off
echo ================================================================================
echo Stock Prediction System - Setup and Run
echo ================================================================================
echo.

echo Step 1: Creating Python virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)
echo Done!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo Done!
echo.

echo Step 3: Installing Python dependencies (this may take 5-10 minutes)...
echo Using --no-cache-dir to avoid permission issues...
pip install --no-cache-dir -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Done!
echo.

echo Step 4: Starting backend server...
echo Backend will run at: http://localhost:8000
echo.
start cmd /k "cd /d %~dp0 && venv\Scripts\activate && python -m backend.main"
echo Backend started in new window!
echo.

timeout /t 3 /nobreak >nul

echo Step 5: Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo Error: Failed to install frontend dependencies
    pause
    exit /b 1
)
echo Done!
echo.

echo Step 6: Starting frontend server...
echo Frontend will run at: http://localhost:3000
echo.
start cmd /k "cd /d %~dp0frontend && npm start"
echo Frontend started in new window!
echo.

echo ================================================================================
echo Setup Complete!
echo ================================================================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Both servers are running in separate windows.
echo Close this window when done.
echo.
pause
