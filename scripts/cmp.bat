@echo off
REM Wrapper script for cmp.py that activates the virtual environment

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set VENV_PATH=%PROJECT_ROOT%\.venv

REM Check if venv exists
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Error: Virtual environment not found at %VENV_PATH% >&2
    exit /b 1
)

REM Activate venv and run the Python script
call "%VENV_PATH%\Scripts\activate.bat" && python "%SCRIPT_DIR%cmp.py" %*
