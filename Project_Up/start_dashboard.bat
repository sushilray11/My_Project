@echo off
cd /d "%~dp0"
echo Starting Project_Up Dashboard on http://localhost:8502
python -m streamlit run app.py --server.port 8502
pause
