@echo off
setlocal

set "PROJECT_DIR=%~dp0abbbb\abbbb\PrivacyPreserving_FaceAuth_HE"
set "VENV_DIR=%LOCALAPPDATA%\PrivacyPreservingFaceAuth\.venv"
if not exist "%PROJECT_DIR%\app.py" (
    echo Could not find the application at:
    echo "%PROJECT_DIR%"
    pause
    exit /b 1
)

pushd "%PROJECT_DIR%"

py -3.12 -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 12) else 1)" >nul 2>&1
if not "%ERRORLEVEL%"=="0" goto :python_missing

if not exist "%VENV_DIR%\Scripts\python.exe" (
    if not exist "%LOCALAPPDATA%\PrivacyPreservingFaceAuth" mkdir "%LOCALAPPDATA%\PrivacyPreservingFaceAuth"
    echo Creating a Python 3.12 virtual environment...
    py -3.12 -m venv "%VENV_DIR%"
    if errorlevel 1 goto :setup_failed

    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :setup_failed
)

if not exist "%VENV_DIR%\requirements.txt" goto :install_requirements
fc /b "requirements.txt" "%VENV_DIR%\requirements.txt" >nul
if errorlevel 1 goto :install_requirements
goto :start_app

:install_requirements
echo Installing project dependencies. This may take several minutes...
    "%VENV_DIR%\Scripts\python.exe" -m pip install --upgrade pip
    if errorlevel 1 goto :setup_failed
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 goto :setup_failed
copy /y "requirements.txt" "%VENV_DIR%\requirements.txt" >nul
if errorlevel 1 goto :setup_failed

:start_app
echo.
echo Starting the local application at http://127.0.0.1:5000
echo Press Ctrl+C to stop the server.
echo.
"%VENV_DIR%\Scripts\python.exe" app.py
set "APP_EXIT_CODE=%ERRORLEVEL%"
popd
if not "%APP_EXIT_CODE%"=="0" pause
exit /b %APP_EXIT_CODE%

:python_missing
echo Python 3.12 (64-bit) was not found by the Python launcher.
echo Install Python 3.12 from https://www.python.org/downloads/
echo Then run this file again.
popd
pause
exit /b 1

:setup_failed
echo Setup failed. Read the error above, resolve it, and run this file again.
popd
pause
exit /b 1
