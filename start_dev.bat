@echo off
echo ============================================
echo    Slippi Stats Development Server
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Trying with 'py' command...
        py -m venv venv
    )
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies from requirements.txt...
    pip install -r requirements.txt
    echo.
)

REM Set development environment
echo Setting up Flask development environment...
set FLASK_ENV=development
set FLASK_DEBUG=1

REM Start the Flask app
echo.
echo Starting Flask development server...
echo Server will be available at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

REM Try different ways to start the app
if exist "app.py" (
    python app.py
) else (
    flask run
)

echo.
echo Server stopped.
pause