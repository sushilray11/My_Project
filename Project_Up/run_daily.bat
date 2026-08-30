@echo off
cd /d "%~dp0"
python daily_run.py >> daily_run.log 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] Run failed with error code %ERRORLEVEL% >> daily_run.log
)
