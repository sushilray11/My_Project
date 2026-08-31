@echo off
cd /d "%~dp0"
echo Starting Combined Dashboard on http://localhost:8500
python -m streamlit run Home.py --server.port 8500
pause
