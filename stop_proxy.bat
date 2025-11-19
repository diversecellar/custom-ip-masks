@echo off
REM Stop Custom IP Masks Proxy Server - Windows Batch Script
REM ========================================================

echo Stopping Custom IP Masks Proxy Server...
echo.
pushd "%~dp0src"

REM Try the simple stop script first (no dependencies)
echo Attempting to stop proxy on default port 8888...
python stop_proxy_simple.py

if %errorlevel% equ 0 (
    echo.
    echo Proxy server stopped successfully!
    pause
    exit /b 0
)

echo.
echo Simple stop failed, trying advanced stop script...
python stop_proxy.py

if %errorlevel% equ 0 (
    echo.
    echo Proxy server stopped successfully!
) else (
    echo.
    echo Failed to stop proxy server automatically
    echo.
    echo Manual options:
    echo 1. Press Ctrl+C in the proxy terminal window
    echo 2. Close the proxy terminal window
    echo 3. Run: taskkill /f /im python.exe
    echo.
)

popd
pause