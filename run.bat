@echo off
chcp 65001 >nul
title RedBook Dictionary - Starter
setlocal

set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

pushd "%SCRIPT_DIR%" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Cannot access this folder.
    echo Please move the files to a normal location (Desktop, Documents, etc).
    pause
    exit /b 1
)

echo.
echo =============================================
echo           REDBOOK DICTIONARY
echo =============================================
echo.

REM ================================================================
REM  STEP 1: Find a REAL Python interpreter (not a Store shortcut)
REM ================================================================
echo [Step 1/4] Finding Python...

set "PY=notfound"

REM Method A: Try py -3 first (Python Launcher - rarely a Store shortcut)
if "%PY%"=="notfound" (
    where py >nul 2>&1
    if !errorlevel! equ 0 (
        py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "PY=py -3"
            for /f "delims=" %%w in ('py -3 --version 2^>^&1') do echo       Found: %%w
        )
    )
)

REM Method B: Try python3
if "%PY%"=="notfound" (
    where python3 >nul 2>&1
    if !errorlevel! equ 0 (
        python3 -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
        if !errorlevel! equ 0 (
            set "PY=python3"
            for /f "delims=" %%w in ('python3 --version 2^>^&1') do echo       Found: %%w
        )
    )
)

REM Method C: Try python, but ONLY if it is a real install (not a Store shortcut)
if "%PY%"=="notfound" (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        REM Run python --version and check output for Store redirect
        for /f "delims=" %%v in ('python --version 2^>^&1') do (
            echo %%v | findstr /i "Microsoft Store" >nul 2>&1
            if !errorlevel! neq 0 (
                REM No Store redirect text - try to use it
                python -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
                if !errorlevel! equ 0 (
                    set "PY=python"
                    for /f "delims=" %%w in ('python --version 2^>^&1') do echo       Found: %%w
                )
            )
        )
    )
)

REM Method D: Check known Python installation paths directly
if "%PY%"=="notfound" (
    for %%p in (
        "C:\Python312\python.exe"
        "C:\Python311\python.exe"
        "C:\Python310\python.exe"
        "C:\Python39\python.exe"
        "C:\Program Files\Python312\python.exe"
        "C:\Program Files\Python311\python.exe"
        "C:\Program Files\Python310\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python311\python.exe"
        "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python310\python.exe"
    ) do (
        if exist %%p (
            %%p -c "import sys; sys.exit(0 if sys.version_info >= (3,8) else 1)" >nul 2>&1
            if !errorlevel! equ 0 (
                set "PY=%%~p"
                for /f "delims=" %%w in ('%%~p --version 2^>^&1') do echo       Found: %%w
            )
        )
    )
)

if "%PY%"=="notfound" goto :install_python
echo.

REM ================================================================
REM  STEP 2: Install Flask if needed (same Python)
REM ================================================================
echo [Step 2/4] Checking Flask...

REM Test that Python actually works (not a Store shortcut)
%PY% -c "print('ok')" >nul 2>&1
if %errorlevel% neq 0 (
    echo       Python seems broken (Store shortcut?). Trying py -3 instead...
    set "PY=py -3"
    %PY% -c "print('ok')" >nul 2>&1
    if %errorlevel% neq 0 (
            goto :install_python
    )
)

%PY% -c "import flask" >nul 2>&1
if %errorlevel% equ 0 (
    echo       Flask: OK
    echo       SQLite3: OK
    echo.
    goto :check_data
)

echo       Flask: NOT installed - installing now
echo       (1-5 minutes, please wait...)
echo.

%PY% -m pip install flask
if %errorlevel% neq 0 (
    echo       Trying --user flag...
    %PY% -m pip install --user flask
)

if %errorlevel% neq 0 (
    echo.
    echo =============================================
    echo           ERROR: Flask install failed
    echo =============================================
    echo.
    echo   1. Network issue - use Chinese mirror:
    echo      %PY% -m pip install flask -i https://pypi.tuna.tsinghua.edu.cn/simple
    echo.
    echo   2. Permission denied:
    echo      Right-click run.bat, choose "Run as administrator"
    echo.
    echo   3. Python version too old:
    echo      %PY% --version
    echo      (need Python 3.8 or higher)
    echo.
    pause
    exit /b 1
)

echo       Flask installed OK
echo.

REM ================================================================
REM  STEP 3: Check data file
REM ================================================================
:check_data
echo [Step 3/4] Checking data files...

if exist data.txt (
    echo       data.txt: OK
) else (
    echo       WARNING: data.txt not found
)
echo.

REM ================================================================
REM  STEP 4: Start server
REM ================================================================
echo [Step 4/4] Starting server...

if not exist app.py (
    echo ERROR: app.py is missing from this folder.
    echo Please re-extract the ZIP file.
    pause
    exit /b 1
)

echo       app.py: OK
echo.
echo ---------------------------------------------
echo   Local:    http://localhost:5000
echo   Network:  http://[PC-IP]:5000
echo   Stop:     Ctrl+C
echo ---------------------------------------------
echo.

timeout /t 2 >nul
start "" http://localhost:5000

%PY% app.py

if %errorlevel% neq 0 (
    echo.
    echo Server stopped. Run this file again if needed.
    pause
)

popd
endlocal
exit /b 0


REM ================================================================
REM  SUB: Install Python
REM ================================================================
:install_python
echo.
echo       Python 3.8+ was NOT found on this system.
echo.
echo =============================================
echo       Attempting auto-install...
echo =============================================
echo.

where winget >nul 2>&1
if %errorlevel% equ 0 (
    echo       Method: winget (Windows Package Manager)
    echo       (You may see a license confirmation popup)
    echo.
    winget install --id Python.Python.3.11 -e --silent --accept-source-agreements --accept-package-agreements
    if %errorlevel% equ 0 (
        echo.
        echo       SUCCESS! Restarting in 5 seconds...
        timeout /t 5 >nul
        start "" "%~f0"
        popd
        endlocal
        exit /b 0
    )
)

echo.
echo Auto-install could not run on this system.
echo.
echo =============================================
echo       Manual Python Installation
echo =============================================
echo.
echo OPTION A -- Microsoft Store (fastest):
echo   1. Open Microsoft Store
echo   2. Search: Python 3.11
echo   3. Click Install
echo   4. After install, run this file again
echo.
echo OPTION B -- python.org:
echo   1. Go to: https://www.python.org/downloads/
echo   2. Download: python-3.11.x-amd64.exe
echo   3. Run the installer
echo   4. CHECK: Add Python to PATH   ^^^^^^^^^^^^^ IMPORTANT!
echo   5. Run this file again
echo.
pause
popd
endlocal
exit /b 1
