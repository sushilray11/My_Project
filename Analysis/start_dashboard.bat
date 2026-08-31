@echo off
cd /d "%~dp0"
echo Starting Analysis Dashboard on http://localhost:8501
python -m streamlit run app.py --server.port 8501
pause
