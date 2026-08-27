@echo off
cd /d "%~dp0"
python daily_export.py
if %ERRORLEVEL% NEQ 0 (
    echo Export failed with error code %ERRORLEVEL%
    pause
)
