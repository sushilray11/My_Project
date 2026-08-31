@echo off
cd /d "%~dp0"
python -c "import streamlit" 2>nul || (
    echo Dependencies not installed. Running setup...
    python -m pip install -r requirements.txt
)
echo Starting Combined Dashboard on http://localhost:8500
python -m streamlit run Home.py --server.port 8500
pause
