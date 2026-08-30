@echo off
cd /d "%~dp0"
python daily_export.py >> exports\export_log.txt 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Export failed with error code %ERRORLEVEL% >> exports\export_log.txt
)
