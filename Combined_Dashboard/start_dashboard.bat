@echo off
cd /d "%~dp0"
python -c "import streamlit, plotly, yfinance, openpyxl, streamlit_autorefresh" 2>nul || (
    echo Installing missing dependencies...
    python -m pip install -r requirements.txt
)
echo Starting Combined Dashboard on http://localhost:8500
python -m streamlit run Home.py --server.port 8500
pause
