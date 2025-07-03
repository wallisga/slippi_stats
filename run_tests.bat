@echo off
echo ============================================
echo    Slippi Stats Test Runner
echo ============================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run start_dev.bat first to create the virtual environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if pytest is installed
echo Checking test dependencies...
pip show pytest >nul 2>&1
if errorlevel 1 (
    echo Installing test dependencies...
    pip install pytest==7.4.0 pytest-flask==1.2.0
    echo.
)

REM Check if tests directory exists
if not exist "tests" (
    echo ERROR: tests directory not found!
    echo Please create the tests/ directory and add test files.
    echo.
    pause
    exit /b 1
)

REM Set test environment variables
echo Setting up test environment...
set FLASK_ENV=testing
set FLASK_DEBUG=0
set PYTHONPATH=%CD%

REM Parse command line arguments for different test options
if "%1"=="quick" goto quick_tests
if "%1"=="api" goto api_tests
if "%1"=="web" goto web_tests
if "%1"=="db" goto db_tests
if "%1"=="service" goto service_tests
if "%1"=="upload" goto upload_tests
if "%1"=="verbose" goto verbose_tests
if "%1"=="coverage" goto coverage_tests

REM Default: Run all tests
echo.
echo Running all tests...
echo.
pytest tests/ -v --tb=short
goto end

:quick_tests
echo.
echo Running quick tests (service layer only)...
echo.
pytest tests/test_service_layer.py -v
goto end

:api_tests
echo.
echo Running API endpoint tests...
echo.
pytest tests/test_api_endpoints.py -v
goto end

:web_tests
echo.
echo Running web page tests...
echo.
pytest tests/test_web_pages.py -v
goto end

:db_tests
echo.
echo Running database tests...
echo.
pytest tests/test_database_simple.py -v
goto end

:service_tests
echo.
echo Running service layer tests...
echo.
pytest tests/test_service_layer.py -v
goto end

:upload_tests
echo.
echo Running upload pipeline tests...
echo.
pytest tests/test_upload_pipeline.py -v
goto end

:verbose_tests
echo.
echo Running all tests with detailed output...
echo.
pytest tests/ -vvv --tb=long
goto end

:coverage_tests
echo.
echo Running tests with coverage report...
echo Checking if pytest-cov is installed...
pip show pytest-cov >nul 2>&1
if errorlevel 1 (
    echo Installing pytest-cov...
    pip install pytest-cov
)
echo.
pytest tests/ --cov=backend --cov-report=html --cov-report=term
echo.
echo Coverage report generated in htmlcov/index.html
goto end

:end
echo.
echo ============================================
if errorlevel 1 (
    echo Tests completed with FAILURES
    echo Check the output above for details
) else (
    echo All tests PASSED!
)
echo ============================================
echo.
echo Usage: run_tests.bat [option]
echo   (no option)  - Run all tests
echo   quick        - Run only service layer tests (fastest)
echo   api          - Run only API endpoint tests  
echo   web          - Run only web page tests
echo   db           - Run only database tests
echo   service      - Run only service layer tests
echo   upload       - Run upload pipeline tests
echo   verbose      - Run all tests with detailed output
echo   coverage     - Run tests with coverage report
echo.
pause