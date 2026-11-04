import streamlit as st
try:
    from streamlit_autorefresh import st_autorefresh
    _has_autorefresh = True
except ImportError:
    _has_autorefresh = False

st.set_page_config(page_title="NSE Trading Dashboard", page_icon="📈", layout="wide")

st.markdown(
    "<style>.block-container{padding-top:1rem!important}</style>",
    unsafe_allow_html=True,
)

# Refresh market ticker every 5 minutes (if package available)
if _has_autorefresh:
    st_autorefresh(interval=300_000, key="home_ticker_refresh")

# ── Top row: title + Nifty/Sensex ticker ─────────────────────────────────────
_hdr_col, _ticker_col = st.columns([3, 1])

with _hdr_col:
    st.title("📈 NSE Trading Dashboard")

with _ticker_col:
    try:
        import yfinance as yf
        _nifty_info  = yf.Ticker("^NSEI").fast_info
        _sensex_info = yf.Ticker("^BSESN").fast_info

        _np  = _nifty_info.last_price
        _npc = _nifty_info.previous_close
        _nch = ((_np - _npc) / _npc * 100) if _npc else 0

        _sp  = _sensex_info.last_price
        _spc = _sensex_info.previous_close
        _sch = ((_sp - _spc) / _spc * 100) if _spc else 0

        def _ticker_html(label, price, chg):
            color  = "#16a34a" if chg >= 0 else "#dc2626"
            arrow  = "▲" if chg >= 0 else "▼"
            sign   = "+" if chg >= 0 else ""
            return (
                f'<div style="margin-bottom:10px">'
                f'  <div style="font-size:11px;color:#6b7280;font-weight:600;letter-spacing:.5px">{label}</div>'
                f'  <span style="font-size:22px;font-weight:700;color:#111">{price:,.2f}</span>'
                f'  <span style="font-size:13px;font-weight:600;color:{color};margin-left:6px">'
                f'    {arrow} {sign}{chg:.2f}%'
                f'  </span>'
                f'</div>'
            )

        st.markdown(
            f'<div style="text-align:right;padding-top:14px">'
            f'{_ticker_html("NIFTY 50", _np, _nch)}'
            f'{_ticker_html("SENSEX", _sp, _sch)}'
            f'</div>',
            unsafe_allow_html=True,
        )
    except Exception:
        st.markdown(
            '<div style="text-align:right;padding-top:14px;color:#9ca3af;font-size:13px">'
            'Market data unavailable</div>',
            unsafe_allow_html=True,
        )

st.markdown("---")

# ── Project cards ─────────────────────────────────────────────────────────────
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
    ### 📈 Trading Setup
    **Short-Term Trading Dashboard**
    - EMA 9/21/50 + RSI + ADX + VWAP signals
    - Candlestick chart with Bollinger Bands
    - Backtest with SL/TP tracking
    - Stock Scanner — BUY/SELL across groups
    - Auto-scan Midcap + Smallcap every 1 hour

    👈 Click **Trading Setup** in the sidebar
    """)

st.markdown("---")
st.caption("Use the sidebar navigation to switch between dashboards.")
