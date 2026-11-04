import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import json
import os

CREDS_FILE = os.path.join(os.path.dirname(__file__), ".creds.json")

def _save_creds(api_key, api_secret, session_token):
    with open(CREDS_FILE, "w") as f:
        json.dump({"api_key": api_key, "api_secret": api_secret, "session_token": session_token}, f)

def _load_creds() -> dict:
    if os.path.exists(CREDS_FILE):
        try:
            with open(CREDS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def _clear_creds():
    if os.path.exists(CREDS_FILE):
        os.remove(CREDS_FILE)
    for k in ("api_key", "api_secret", "session_token"):
        st.session_state.pop(k, None)

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="My Portfolio Dashboard",
    page_icon="📈",
    layout="wide",
)

# ── Palette (dataviz skill — validated) ────────────────────────────────────────
BLUE       = "#2a78d6"
ORANGE     = "#eb6834"
AQUA       = "#1baf7a"
YELLOW     = "#eda100"
GAIN_CLR   = "#0ca30c"
LOSS_CLR   = "#d03b3b"
SURFACE    = "#fcfcfb"
TEXT_PRI   = "#0b0b0b"
TEXT_SEC   = "#52514e"
GRID       = "#e1e0d9"

CATEGORICAL = [BLUE, ORANGE, AQUA, YELLOW, "#e87ba4", "#008300", "#4a3aa7", "#e34948"]

# ── NSE sector map ─────────────────────────────────────────────────────────────
SECTOR_MAP = {
    # Financial Services
    "HDFCBANK":"Financial Services","ICICIBANK":"Financial Services",
    "KOTAKBANK":"Financial Services","SBIN":"Financial Services",
    "AXISBANK":"Financial Services","BAJFINANCE":"Financial Services",
    "BAJAJFINSV":"Financial Services","SBILIFE":"Financial Services",
    "HDFCLIFE":"Financial Services","ICICIGI":"Financial Services",
    "MUTHOOTFIN":"Financial Services","CHOLAFIN":"Financial Services",
    "BANDHANBNK":"Financial Services","FEDERALBNK":"Financial Services",
    "IDFCFIRSTB":"Financial Services","PNB":"Financial Services",
    "BANKBARODA":"Financial Services","CANBK":"Financial Services",
    "INDUSINDBK":"Financial Services","RBLBANK":"Financial Services",
    # IT
    "TCS":"Information Technology","INFY":"Information Technology",
    "WIPRO":"Information Technology","HCLTECH":"Information Technology",
    "TECHM":"Information Technology","LTI":"Information Technology",
    "LTIM":"Information Technology","MPHASIS":"Information Technology",
    "PERSISTENT":"Information Technology","COFORGE":"Information Technology",
    "OFSS":"Information Technology","KPITTECH":"Information Technology",
    # Oil & Gas
    "RELIANCE":"Oil & Gas","ONGC":"Oil & Gas","IOC":"Oil & Gas",
    "BPCL":"Oil & Gas","GAIL":"Oil & Gas","HINDPETRO":"Oil & Gas",
    "OIL":"Oil & Gas","PETRONET":"Oil & Gas","MGL":"Oil & Gas",
    # Consumer
    "HINDUNILVR":"Consumer Goods","ITC":"Consumer Goods",
    "NESTLEIND":"Consumer Goods","BRITANNIA":"Consumer Goods",
    "DABUR":"Consumer Goods","MARICO":"Consumer Goods",
    "GODREJCP":"Consumer Goods","COLPAL":"Consumer Goods",
    "EMAMILTD":"Consumer Goods","TATACONSUM":"Consumer Goods",
    "VARUNBEV":"Consumer Goods","VBL":"Consumer Goods",
    # Automobile
    "MARUTI":"Automobile","TATAMOTORS":"Automobile",
    "M&M":"Automobile","BAJAJ-AUTO":"Automobile",
    "HEROMOTOCO":"Automobile","EICHERMOT":"Automobile",
    "ASHOKLEY":"Automobile","TVSMOTOR":"Automobile",
    "MOTHERSON":"Automobile","BOSCHLTD":"Automobile",
    # Pharma
    "SUNPHARMA":"Pharma","DRREDDY":"Pharma","CIPLA":"Pharma",
    "DIVISLAB":"Pharma","BIOCON":"Pharma","AUROPHARMA":"Pharma",
    "ALKEM":"Pharma","TORNTPHARM":"Pharma","IPCALAB":"Pharma",
    "LUPIN":"Pharma","GLENMARK":"Pharma","ABBOTINDIA":"Pharma",
    # Metals & Mining
    "TATASTEEL":"Metals & Mining","HINDALCO":"Metals & Mining",
    "JSWSTEEL":"Metals & Mining","VEDL":"Metals & Mining",
    "COALINDIA":"Metals & Mining","NMDC":"Metals & Mining",
    "SAIL":"Metals & Mining","NATIONALUM":"Metals & Mining",
    "HINDCOPPER":"Metals & Mining","APLAPOLLO":"Metals & Mining",
    # Telecom
    "BHARTIARTL":"Telecom","IDEA":"Telecom","TTML":"Telecom",
    # Power & Energy
    "POWERGRID":"Power","NTPC":"Power","TATAPOWER":"Power",
    "ADANIPOWER":"Power","ADANIGREEN":"Power","CESC":"Power",
    "TORNTPOWER":"Power","NHPC":"Power","SJVN":"Power",
    # Cement
    "ULTRACEMCO":"Cement","SHREECEM":"Cement","ACC":"Cement",
    "AMBUJACEM":"Cement","DALBHARAT":"Cement","RAMCOCEM":"Cement",
    "HEIDELBERG":"Cement",
    # Healthcare
    "APOLLOHOSP":"Healthcare","FORTIS":"Healthcare",
    "MAXHEALTH":"Healthcare","MEDANTA":"Healthcare",
    "METROPOLIS":"Healthcare","LALPATHLAB":"Healthcare",
    # Infrastructure & Real Estate
    "ADANIPORTS":"Infrastructure","DLF":"Real Estate",
    "GODREJPROP":"Real Estate","OBEROIRLTY":"Real Estate",
    "PRESTIGE":"Real Estate","PHOENIXLTD":"Real Estate",
    "BRIGADE":"Real Estate",
    # Capital Goods
    "LT":"Capital Goods","SIEMENS":"Capital Goods",
    "ABB":"Capital Goods","BHEL":"Capital Goods",
    "HAVELLS":"Capital Goods","POLYCAB":"Capital Goods",
    "CUMMINSIND":"Capital Goods","THERMAX":"Capital Goods",
    # Chemicals
    "PIDILITIND":"Chemicals","ASIANPAINT":"Chemicals",
    "BERGERPAINTS":"Chemicals","KANSAINER":"Chemicals",
    "AARTIIND":"Chemicals","DEEPAKNTR":"Chemicals",
    "NAVINFLUOR":"Chemicals","SRF":"Chemicals",
    # Aviation & Logistics
    "INDIGO":"Aviation","BLUEDART":"Logistics",
    "CONCOR":"Logistics","DELHIVERY":"Logistics",
    # Media & Entertainment
    "ZEEL":"Media","SUNTV":"Media","PVRINOX":"Media",
}

def _get_sector(stock_code: str, holding: dict) -> str:
    # Check API-returned field first
    for field in ("sector_name", "sector", "industry_name", "industry"):
        val = holding.get(field, "")
        if val:
            return val.strip().title()
    return SECTOR_MAP.get(stock_code.upper(), "Others")

# ── Company name fallback map ──────────────────────────────────────────────────
COMPANY_MAP = {
    "APMFIN":  "APM Finvest Ltd",
    "MINCOR":  "Mincorp Ltd",
    "WATLEI":  "Waterbase Ltd",
    "JARTEX":  "Jartex India Ltd",
    "TRIDRU":  "Tridrug Pharma Ltd",
    "EMULIM":  "Emulsion Ltd",
    "RUBRES":  "Rubber Resources Ltd",
    "SIGIN":   "Sig Industries Ltd",
    "POLCOR":  "Poly Corp Ltd",
    "BELLIM":  "Bell Industries Ltd",
    "RAGRAM":  "Ragram Ltd",
}

def _get_company(stock_code: str, holding: dict) -> str:
    name = holding.get("company_name", "").strip()
    if name and name.upper() != stock_code.upper():
        return name
    return COMPANY_MAP.get(stock_code.upper(), stock_code)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stSidebar"] { background: #f5f5f3; }
  .stat-card {
      background: #fcfcfb;
      border: 1px solid #e1e0d9;
      border-radius: 10px;
      padding: 18px 22px;
      text-align: center;
  }
  .stat-label { font-size: 13px; color: #52514e; font-weight: 500; margin-bottom: 4px; }
  .stat-value { font-size: 26px; font-weight: 700; color: #0b0b0b; }
  .stat-delta { font-size: 13px; font-weight: 600; margin-top: 4px; }
  .gain  { color: #006300; }
  .loss  { color: #d03b3b; }
  .neutral { color: #52514e; }
  div[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar — credentials ──────────────────────────────────────────────────────
# Seed session state from saved file (runs only once per browser session)
if "api_key" not in st.session_state:
    saved = _load_creds()
    st.session_state["api_key"]       = saved.get("api_key", "")
    st.session_state["api_secret"]    = saved.get("api_secret", "")
    st.session_state["session_token"] = saved.get("session_token", "")

with st.sidebar:
    st.markdown("## 🔑 ICICIdirect Credentials")
    api_key       = st.text_input("API Key",       type="password",
                                  value=st.session_state["api_key"],
                                  placeholder="Paste your API Key")
    api_secret    = st.text_input("API Secret",    type="password",
                                  value=st.session_state["api_secret"],
                                  placeholder="Paste your API Secret")
    session_token = st.text_input("Session Token", type="password",
                                  value=st.session_state["session_token"],
                                  placeholder="Paste session token")

    with st.expander("How to get the Session Token"):
        st.markdown("""
1. Open this URL in a browser (replace with your key):
   ```
   https://api.icicidirect.com/apiuser/login?api_key=YOUR_API_KEY
   ```
2. Log in with your ICICIdirect credentials.
3. After login you will be redirected — copy the **session_token** value from the URL.
4. Paste it in the field above.
        """)

    connect = st.button("🔌 Connect & Load Portfolio", type="primary", use_container_width=True)

    if os.path.exists(CREDS_FILE):
        if st.button("🗑 Clear saved credentials", use_container_width=True):
            _clear_creds()
            st.rerun()
        st.caption("✅ Credentials loaded from last session.")
    else:
        st.caption("Credentials will be saved locally after you connect.")


# ── Helper — format Indian currency ───────────────────────────────────────────
def fmt_inr(val: float) -> str:
    if abs(val) >= 1_00_00_000:
        return f"₹{val/1_00_00_000:.2f} Cr"
    if abs(val) >= 1_00_000:
        return f"₹{val/1_00_000:.2f} L"
    return f"₹{val:,.0f}"


def color_pnl(val: float) -> str:
    if val > 0:
        return "gain"
    if val < 0:
        return "loss"
    return "neutral"


def stat_card(label: str, value: str, delta: str = "", delta_class: str = "neutral") -> str:
    delta_html = f'<div class="stat-delta {delta_class}">{delta}</div>' if delta else ""
    return f"""
    <div class="stat-card">
        <div class="stat-label">{label}</div>
        <div class="stat-value">{value}</div>
        {delta_html}
    </div>"""


# ── Main ───────────────────────────────────────────────────────────────────────
st.title("📊 My Portfolio Dashboard")
st.caption("Powered by ICICIdirect Breeze Connect API")

# Auto-connect on reruns (e.g. after download button click) if already connected
_already_connected = st.session_state.get("breeze_connected", False)
_has_creds = bool(api_key and api_secret and session_token)

if not connect and not _already_connected:
    st.info("Enter your ICICIdirect API credentials in the sidebar and click **Connect & Load Portfolio** to begin.")
    st.stop()

if not _has_creds:
    st.error("Please fill in all three credential fields (API Key, API Secret, Session Token).")
    st.stop()

# ── Connect to Breeze ──────────────────────────────────────────────────────────
with st.spinner("Connecting to ICICIdirect…"):
    try:
        from breeze_connect import BreezeConnect
        breeze = BreezeConnect(api_key=api_key)
        breeze.generate_session(api_secret=api_secret, session_token=session_token)
        _save_creds(api_key, api_secret, session_token)
        st.session_state["api_key"]         = api_key
        st.session_state["api_secret"]      = api_secret
        st.session_state["session_token"]   = session_token
        st.session_state["breeze_connected"] = True
    except Exception as e:
        st.error(f"Connection failed: {e}")
        _clear_creds()
        st.session_state["breeze_connected"] = False
        st.stop()

# ── Fetch holdings (NSE + BSE) ─────────────────────────────────────────────────
with st.spinner("Fetching portfolio holdings…"):
    raw = []
    errors = []
    for exchange in ["NSE", "BSE"]:
        try:
            resp = breeze.get_portfolio_holdings(exchange_code=exchange)
            if resp.get("Status") == 200 and resp.get("Success"):
                holdings = resp["Success"]
                if isinstance(holdings, list):
                    raw.extend(holdings)
                elif isinstance(holdings, dict):
                    raw.append(holdings)
        except Exception as e:
            errors.append(f"{exchange}: {e}")

    if not raw:
        st.warning("No holdings found across NSE and BSE.")
        if errors:
            st.error("Errors encountered: " + " | ".join(errors))
        st.stop()

# ── Build DataFrame ────────────────────────────────────────────────────────────
# The API returns the full portfolio for each exchange_code call, so deduplicate
# by stock_code, preferring NSE over BSE when both appear.
seen: dict = {}
for h in raw:
    key      = h.get("stock_code", "").upper()
    exchange = h.get("exchange_code", "")
    if key not in seen or exchange == "NSE":
        seen[key] = h

# ── Fetch live quotes for each holding ────────────────────────────────────────
def _extract_price(data: dict) -> tuple:
    """Return (price, price_type) from a get_quotes response dict."""
    ltp = float(data.get("ltp", 0) or data.get("last_trade_price", 0) or 0)
    if ltp:
        return ltp, "live"
    prev = float(
        data.get("previous_close", 0)
        or data.get("prev_close", 0)
        or data.get("close", 0)
        or data.get("last_close", 0)
        or 0
    )
    if prev:
        return prev, "prev_close"
    return 0.0, ""

def _fetch_quote(breeze, stock_code: str, exchange: str) -> tuple:
    """Try get_quotes with cash then empty product_type; return (price, price_type)."""
    for product_type in ["cash", ""]:
        try:
            q = breeze.get_quotes(
                stock_code=stock_code,
                exchange_code=exchange,
                expiry_date="",
                product_type=product_type,
                right="others",
                strike_price="0",
            )
            if q.get("Status") == 200 and q.get("Success"):
                price, ptype = _extract_price(q["Success"][0])
                if price:
                    return price, ptype
        except Exception:
            pass
    return 0.0, ""

def _fetch_historical_close(breeze, stock_code: str, exchange: str) -> float:
    """Return the most recent daily close from historical data (last 7 days)."""
    from datetime import datetime, timedelta
    try:
        to_dt   = datetime.now()
        from_dt = to_dt - timedelta(days=7)
        r = breeze.get_historical_data_v2(
            interval="1day",
            from_date=from_dt.strftime("%Y-%m-%dT07:00:00.000Z"),
            to_date=to_dt.strftime("%Y-%m-%dT15:30:00.000Z"),
            stock_code=stock_code,
            exchange_code=exchange,
            product_type="cash",
        )
        if r.get("Status") == 200 and r.get("Success"):
            return float(r["Success"][-1].get("close", 0) or 0)
    except Exception:
        pass
    return 0.0

with st.spinner("Fetching live prices…"):
    for key, h in seen.items():
        primary   = h.get("exchange_code", "NSE")
        secondary = "BSE" if primary == "NSE" else "NSE"

        # 1. Live/prev-close from primary exchange
        price, ptype = _fetch_quote(breeze, key, primary)

        # 2. Retry on the other exchange
        if not price:
            price, ptype = _fetch_quote(breeze, key, secondary)

        # 3. Historical daily close — primary exchange
        if not price:
            price = _fetch_historical_close(breeze, key, primary)
            if price:
                ptype = "prev_close"

        # 4. Historical daily close — secondary exchange
        if not price:
            price = _fetch_historical_close(breeze, key, secondary)
            if price:
                ptype = "prev_close"

        # 5. previous_close field on the holdings record itself
        if not price:
            price = float(
                h.get("previous_close", 0) or h.get("prev_close", 0)
                or h.get("close", 0) or 0
            )
            if price:
                ptype = "prev_close"

        if price:
            h["ltp"]        = price
            h["price_type"] = ptype

rows = []
for key, h in seen.items():
    qty        = float(h.get("quantity", 0) or 0)
    avg        = float(h.get("average_price", 0) or 0)
    ltp        = float(h.get("ltp", 0) or h.get("current_price", 0) or 0)
    price_type = h.get("price_type", "")   # "live", "prev_close", or ""
    if qty == 0:
        continue
    invested    = qty * avg
    current_val = qty * ltp if ltp else invested
    pnl         = current_val - invested
    pnl_pct     = (pnl / invested * 100) if invested else 0

    price_label = ""
    if price_type == "prev_close":
        price_label = " *"
    elif not ltp:
        price_label = " —"

    rows.append({
        "Stock":             key,
        "Company":           _get_company(key, h),
        "Sector":            _get_sector(key, h),
        "Qty":               int(qty),
        "Buy Price (₹)":     round(avg, 2),
        "Current Price (₹)": (str(round(ltp, 2)) + price_label) if ltp else "—",
        "Invested (₹)":      round(invested, 2),
        "Current Value (₹)": round(current_val, 2),
        "P&L (₹)":           round(pnl, 2),
        "Return (%)":        round(pnl_pct, 2),
    })

if not rows:
    st.warning("Holdings list is empty after processing.")
    st.stop()

df = pd.DataFrame(rows).sort_values("Invested (₹)", ascending=False).reset_index(drop=True)

# ── Portfolio-level summary ────────────────────────────────────────────────────
total_invested = df["Invested (₹)"].sum()
total_current  = df["Current Value (₹)"].sum()
total_pnl      = total_current - total_invested
total_pnl_pct  = (total_pnl / total_invested * 100) if total_invested else 0
num_stocks     = len(df)
gainers        = (df["P&L (₹)"] > 0).sum()
losers         = (df["P&L (₹)"] < 0).sum()

pnl_sign  = "▲" if total_pnl >= 0 else "▼"
pnl_class = color_pnl(total_pnl)

# ── Stat tiles row ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(stat_card("Total Invested", fmt_inr(total_invested)), unsafe_allow_html=True)
with c2:
    st.markdown(stat_card("Current Value", fmt_inr(total_current)), unsafe_allow_html=True)
with c3:
    st.markdown(
        stat_card(
            "Total P&L",
            fmt_inr(total_pnl),
            f"{pnl_sign} {abs(total_pnl_pct):.2f}%",
            pnl_class,
        ),
        unsafe_allow_html=True,
    )
with c4:
    st.markdown(
        stat_card("Holdings", str(num_stocks), f"{gainers} gainers · {losers} losers", "neutral"),
        unsafe_allow_html=True,
    )

st.divider()

# ── Portfolio vs NIFTY 50 ─────────────────────────────────────────────────────
st.subheader("Portfolio vs NIFTY 50")

def _nifty_data(breeze) -> tuple:
    """Return (time_series_df, period_returns_dict) for NIFTY 50."""
    from datetime import datetime, timedelta
    periods = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365}
    try:
        today     = datetime.now()
        from_date = today - timedelta(days=370)
        raw = []
        for product_type in ["cash", "index", ""]:
            r = breeze.get_historical_data_v2(
                interval="1day",
                from_date=from_date.strftime("%Y-%m-%dT07:00:00.000Z"),
                to_date=today.strftime("%Y-%m-%dT15:30:00.000Z"),
                stock_code="NIFTY",
                exchange_code="NSE",
                product_type=product_type,
            )
            if r.get("Status") == 200 and r.get("Success"):
                raw = r["Success"]
                if raw:
                    break
        if not raw:
            return None, {}

        # Build a clean DataFrame
        ts = pd.DataFrame([{
            "date":  d.get("datetime", d.get("date", ""))[:10],
            "close": float(d.get("close", 0) or 0),
        } for d in raw if d.get("close")])
        ts["date"] = pd.to_datetime(ts["date"])
        ts = ts.sort_values("date").drop_duplicates("date").reset_index(drop=True)

        # % return from the first date in the series (baseline = 0)
        base_close = ts["close"].iloc[0]
        ts["pct"] = (ts["close"] - base_close) / base_close * 100

        # Period returns vs today's close
        latest = ts["close"].iloc[-1]
        period_rets = {}
        for label, days in periods.items():
            cutoff = today - timedelta(days=days)
            past = ts[ts["date"] <= cutoff]
            if not past.empty:
                period_rets[label] = round((latest - past["close"].iloc[-1]) / past["close"].iloc[-1] * 100, 2)

        return ts, period_rets
    except Exception:
        return None, {}

with st.spinner("Fetching NIFTY 50 data…"):
    nifty_ts, nifty = _nifty_data(breeze)

if nifty_ts is not None and not nifty_ts.empty:
    periods_order = ["1M", "3M", "6M", "1Y"]
    nifty_labels  = [p for p in periods_order if nifty.get(p) is not None]

    col_chart, col_tiles = st.columns([1.6, 1], gap="large")

    with col_chart:
        nifty_vals  = [nifty.get(p) for p in nifty_labels]
        bar_colors  = [GAIN_CLR if v >= 0 else LOSS_CLR for v in nifty_vals]
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=nifty_labels,
            y=nifty_vals,
            name="NIFTY 50",
            marker=dict(color=bar_colors, line=dict(width=0)),
            hovertemplate="NIFTY 50 %{x}: <b>%{y:+.2f}%</b><extra></extra>",
        ))

        fig.add_hline(
            y=total_pnl_pct,
            line=dict(color=BLUE, width=2, dash="dash"),
            annotation_text=f"  Your Portfolio ({total_pnl_pct:+.2f}%)",
            annotation_position="top left",
            annotation_font=dict(color=BLUE, size=12),
        )

        fig.update_layout(
            paper_bgcolor=SURFACE,
            plot_bgcolor=SURFACE,
            font=dict(family="system-ui, -apple-system, sans-serif", color=TEXT_PRI),
            xaxis=dict(gridcolor="rgba(0,0,0,0)", tickfont=dict(size=12)),
            yaxis=dict(
                gridcolor=GRID,
                ticksuffix="%",
                zerolinecolor="#c3c2b7",
                tickfont=dict(color=TEXT_SEC, size=11),
            ),
            legend=dict(orientation="h", y=1.08),
            margin=dict(t=40, b=30, l=10, r=10),
            height=300,
            bargap=0.45,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_tiles:
        st.markdown("<br>", unsafe_allow_html=True)
        for label in nifty_labels:
            nval = nifty[label]
            diff = round(total_pnl_pct - nval, 2)
            sign = "▲" if diff >= 0 else "▼"
            cls  = "gain" if diff >= 0 else "loss"
            st.markdown(
                stat_card(
                    f"NIFTY 50 {label}",
                    f"{nval:+.2f}%",
                    f"{sign} {abs(diff):.2f}% vs your portfolio",
                    cls,
                ),
                unsafe_allow_html=True,
            )
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
else:
    st.info("Could not fetch NIFTY 50 data. The comparison will appear once market data is available.")

st.divider()

# ── Uptrend stocks (last 1 month) ─────────────────────────────────────────────
st.subheader("📈 Stocks in Uptrend — Last 1 Month")

def _classify_trend(breeze, stock_code: str, exchange: str):
    """Fetch 90 days of daily data and classify trend + long-term score."""
    from datetime import datetime, timedelta
    try:
        today   = datetime.now()
        from_dt = today - timedelta(days=95)
        raw = []
        for product_type in ["cash", ""]:
            r = breeze.get_historical_data_v2(
                interval="1day",
                from_date=from_dt.strftime("%Y-%m-%dT07:00:00.000Z"),
                to_date=today.strftime("%Y-%m-%dT15:30:00.000Z"),
                stock_code=stock_code,
                exchange_code=exchange,
                product_type=product_type,
            )
            if r.get("Status") == 200 and r.get("Success"):
                raw = r["Success"]
                if len(raw) >= 10:
                    break
        if len(raw) < 10:
            return None

        closes = [float(d.get("close", 0)) for d in raw if d.get("close")]
        if len(closes) < 10:
            return None

        current   = closes[-1]
        month_ago = closes[max(0, len(closes) - 22)]
        qtr_ago   = closes[0]

        # ── Short-term indicators (uptrend) ───────────────────────────────────
        sma20       = sum(closes[-20:]) / min(20, len(closes))
        sma_recent  = sum(closes[-5:]) / 5
        sma_prev    = sum(closes[-10:-5]) / 5
        sma20_rising = sma_recent > sma_prev
        one_month_return = round((current - month_ago) / month_ago * 100, 2) if month_ago else 0
        is_uptrend = current > sma20 and sma20_rising and one_month_return > 0

        # ── Long-term indicators ──────────────────────────────────────────────
        sma50 = sum(closes[-50:]) / min(50, len(closes)) if len(closes) >= 20 else sma20
        sma50_recent = sum(closes[-5:]) / 5
        sma50_prev   = sum(closes[-15:-10]) / 5 if len(closes) >= 15 else sma50_prev if False else sma50
        sma50_rising = sma50_recent > sma50_prev

        three_month_return = round((current - qtr_ago) / qtr_ago * 100, 2) if qtr_ago else 0

        # Annualised volatility (std dev of daily returns * sqrt(252))
        daily_returns = [(closes[i] - closes[i-1]) / closes[i-1]
                         for i in range(1, len(closes)) if closes[i-1]]
        if daily_returns:
            mean_r = sum(daily_returns) / len(daily_returns)
            variance = sum((r - mean_r) ** 2 for r in daily_returns) / len(daily_returns)
            ann_vol = (variance ** 0.5) * (252 ** 0.5) * 100
        else:
            ann_vol = 999

        # RSI-14
        gains = [max(closes[i] - closes[i-1], 0) for i in range(1, len(closes))]
        losses = [max(closes[i-1] - closes[i], 0) for i in range(1, len(closes))]
        avg_gain = sum(gains[-14:]) / 14 if len(gains) >= 14 else 0
        avg_loss = sum(losses[-14:]) / 14 if len(losses) >= 14 else 0
        rsi = 100 - (100 / (1 + avg_gain / avg_loss)) if avg_loss else 100

        # ── Long-term score (0–5) ─────────────────────────────────────────────
        score = sum([
            current > sma50,                       # above 50-day SMA
            sma50_rising,                           # 50-day SMA trending up
            three_month_return > 5,                 # 3M return > 5%
            ann_vol < 35,                           # low volatility
            40 <= rsi <= 65,                        # RSI in healthy entry zone
        ])

        return {
            "uptrend":            is_uptrend,
            "1M Return (%)":      one_month_return,
            "3M Return (%)":      three_month_return,
            "Current Price":      round(current, 2),
            "SMA 20":             round(sma20, 2),
            "SMA 50":             round(sma50, 2),
            "Above SMA20":        "✅" if current > sma20 else "❌",
            "Above SMA50":        "✅" if current > sma50 else "❌",
            "SMA Rising":         "✅" if sma20_rising else "❌",
            "RSI":                round(rsi, 1),
            "Volatility (%)":     round(ann_vol, 1),
            "LT Score":           score,
        }
    except Exception:
        return None

with st.spinner("Analysing trends for all holdings…"):
    trend_rows = []
    for _, row in df.iterrows():
        exchange = seen.get(row["Stock"], {}).get("exchange_code", "NSE")
        result   = _classify_trend(breeze, row["Stock"], exchange)
        if result and result["uptrend"]:
            trend_rows.append({
                "Stock":             row["Stock"],
                "Company":           row["Company"],
                "Buy Price (₹)":     row["Buy Price (₹)"],
                "Current Price (₹)": result["Current Price"],
                "1M Return (%)":     result["1M Return (%)"],
                "3M Return (%)":     result["3M Return (%)"],
                "RSI":               result["RSI"],
                "Volatility (%)":    result["Volatility (%)"],
                "Above SMA20":       result["Above SMA20"],
                "Above SMA50":       result["Above SMA50"],
                "LT Score":          result["LT Score"],
            })

if trend_rows:
    trend_df = (
        pd.DataFrame(trend_rows)
        .sort_values("1M Return (%)", ascending=False)
        .reset_index(drop=True)
    )
    trend_df.index += 1

    def _fmt_trend(df_in):
        return (
            df_in.style
            .format({
                "Buy Price (₹)":     "₹{:,.2f}",
                "Current Price (₹)": "₹{:,.2f}",
                "1M Return (%)":     "{:+.2f}%",
                "3M Return (%)":     "{:+.2f}%",
                "RSI":               "{:.1f}",
                "Volatility (%)":    "{:.1f}%",
            })
            .applymap(lambda v: "color:#006300;font-weight:600"
                      if isinstance(v, float) and v > 0 else
                      "color:#d03b3b;font-weight:600"
                      if isinstance(v, float) and v < 0 else "",
                      subset=["1M Return (%)", "3M Return (%)"])
        )

    # ── Best for Long Term (score >= 4) ───────────────────────────────────────
    lt_df = trend_df[trend_df["LT Score"] >= 4].copy().reset_index(drop=True)
    lt_df = lt_df.drop(columns=["Company"], errors="ignore")
    lt_df.index += 1

    if not lt_df.empty:
        st.markdown("### ⭐ Best for Long Term")
        st.caption("Stocks scoring 4–5 out of 5: above 50-day SMA, SMA rising, 3M return > 5%, low volatility, RSI 40–65")
        st.dataframe(_fmt_trend(lt_df), use_container_width=True,
                     height=min(400, 56 + len(lt_df) * 35))

        import io as _io
        lt_buf = _io.BytesIO()
        with pd.ExcelWriter(lt_buf, engine="openpyxl") as _w:
            lt_df.reset_index(drop=True).to_excel(_w, sheet_name="Best for Long Term", index=False)
        lt_buf.seek(0)
        st.download_button(
            label="⬇ Export Best for Long Term to Excel",
            data=lt_buf,
            file_name="best_long_term_stocks.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    # ── All uptrend stocks ────────────────────────────────────────────────────
    st.markdown("### All Uptrend Stocks")
    st.dataframe(_fmt_trend(trend_df), use_container_width=True,
                 height=min(500, 56 + len(trend_df) * 35))
    st.caption(
        f"{len(trend_rows)} of {len(df)} holdings in uptrend  •  "
        f"{len(lt_df)} best for long term  •  "
        "LT Score: /5 (above SMA50 + SMA rising + 3M>5% + low vol + RSI 40–65)"
    )

    # ── Excel export ──────────────────────────────────────────────────────────
    import io
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        if not lt_df.empty:
            lt_df.reset_index(drop=True).to_excel(writer, sheet_name="Best for Long Term", index=False)
        trend_df.reset_index(drop=True).to_excel(writer, sheet_name="All Uptrend Stocks", index=False)
        df.reset_index(drop=True).to_excel(writer, sheet_name="Full Holdings", index=False)
    buf.seek(0)

    st.download_button(
        label="⬇ Export to Excel",
        data=buf,
        file_name="my_portfolio_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
else:
    st.info("No holdings meet the uptrend criteria at this time.")

st.divider()

# ── Holdings table ─────────────────────────────────────────────────────────────
st.subheader("Holdings Detail")

# Colour-code P&L column
def highlight_pnl(val):
    if isinstance(val, float):
        if val > 0:
            return "color: #006300; font-weight: 600"
        if val < 0:
            return "color: #d03b3b; font-weight: 600"
    return ""

display_df = df.copy()
display_df.index = display_df.index + 1  # 1-based row index

styled = (
    display_df
    .style
    .applymap(highlight_pnl, subset=["P&L (₹)", "Return (%)"])
    .format({
        "Buy Price (₹)":     "₹{:,.2f}",
        "Invested (₹)":      "₹{:,.2f}",
        "Current Value (₹)": "₹{:,.2f}",
        "P&L (₹)":           "₹{:,.2f}",
        "Return (%)":        "{:+.2f}%",
    })
    .set_properties(**{"text-align": "right"}, subset=[
        "Qty", "Buy Price (₹)", "Current Price (₹)",
        "Invested (₹)", "Current Value (₹)", "P&L (₹)", "Return (%)",
    ])
)

st.dataframe(styled, use_container_width=True, height=min(600, 56 + len(df) * 35))
st.caption("\\* Previous closing price (live price unavailable)")

# ── Download ───────────────────────────────────────────────────────────────────
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="⬇ Download as CSV",
    data=csv,
    file_name="my_portfolio.csv",
    mime="text/csv",
)
