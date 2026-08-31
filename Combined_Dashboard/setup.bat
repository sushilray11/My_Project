@echo off
cd /d "%~dp0"
echo Installing required packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo.
echo Setup complete. Run start_dashboard.bat to launch.
pause
