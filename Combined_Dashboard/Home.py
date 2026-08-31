import streamlit as st

st.set_page_config(page_title="NSE Trading Dashboard", page_icon="📈", layout="wide")

st.title("📈 NSE Trading Dashboard")
st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### 📊 Analysis
    **NSE F&O Screener**
    - Probable Upside candidates
    - Support Entry setups
    - Consolidation Breakout setups
    - Backtest (last 7 dates)
    - NSE F&O Stocks list

    👈 Click **Analysis** in the sidebar
    """)

with col2:
    st.markdown("""
    ### 🚀 Project Up
    **NSE Equity Screener**
    - Full NSE universe (~2200 stocks)
    - 10-signal PVA scoring model
    - Top 20 high-conviction setups
    - Backtest (last 10 dates)

    👈 Click **Project Up** in the sidebar
    """)

with col3:
    st.markdown("""
    ### 🏠 My Dashboard
    **Personal Dashboard**
    - Portfolio & watchlist tracking
    - Custom views and metrics

    👈 Click **My Dashboard** in the sidebar
    """)

st.markdown("---")
st.caption("Use the sidebar navigation to switch between dashboards.")
