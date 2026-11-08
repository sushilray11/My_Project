import streamlit as st
try:
    from streamlit_autorefresh import st_autorefresh
    _has_autorefresh = True
except ImportError:
    _has_autorefresh = False

st.set_page_config(page_title="NSE Trading Dashboard", page_icon="📈", layout="wide")

st.markdown("""
<style>
.block-container{padding-top:0.4rem!important;padding-bottom:0.5rem!important}
h1{margin-bottom:0!important;padding-bottom:0!important}
.stHorizontalBlock{gap:0.5rem!important}
</style>""", unsafe_allow_html=True)

# Refresh market ticker every 5 minutes (if package available)
if _has_autorefresh:
    st_autorefresh(interval=300_000, key="home_ticker_refresh")

# ── Title ─────────────────────────────────────────────────────────────────────
st.markdown("<h1 style='font-size:1.8rem;margin:0;padding:0;line-height:1.2'>📈 NSE Trading Dashboard</h1>",
            unsafe_allow_html=True)
st.markdown("---")


# ── Markets at a Glance ───────────────────────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def _fetch_markets():
    import yfinance as yf
    items = [
        ("📊 India VIX",      "^INDIAVIX",          "vix", 1),
        ("🇮🇳 Nifty 50",       "^NSEI",              "idx", 1),
        ("🇮🇳 Sensex",        "^BSESN",             "idx", 1),
        ("🇮🇳 Midcap 100",    "NIFTY_MIDCAP_100.NS","idx", 1),
        ("🇮🇳 Smallcap 250",  "^CNXSC",             "idx", 1),
        ("🇺🇸 Dow",           "^DJI",               "idx", 2),
        ("🇺🇸 Nasdaq",        "^IXIC",              "idx", 2),
        ("🇺🇸 S&P 500",       "^GSPC",              "idx", 2),
        ("🇯🇵 Nikkei",        "^N225",              "idx", 2),
        ("🇰🇷 KOSPI",         "^KS11",              "idx", 2),
        ("📈 S&P Fut",         "ES=F",               "idx", 3),
        ("📈 Nasdaq Fut",      "NQ=F",               "idx", 3),
        ("📈 Dow Fut",         "YM=F",               "idx", 3),
        ("🛢 Brent",           "BZ=F",               "com", 3),
        ("🥇 Gold",            "GC=F",               "com", 3),
        ("💵 USD/INR",         "USDINR=X",           "fx",  4),
    ]
    out = []
    for label, sym, kind, row in items:
        price, chg = None, 0.0
        try:
            t  = yf.Ticker(sym)
            fi = t.fast_info
            if sym.endswith("=F"):
                # Futures trade nearly 24h. Compare live price to previous
                # settlement. The tricky part: when viewing from India in the
                # morning, no US daily bar for today may exist yet (pre-market).
                # If the last bar is today (ET) → use iloc[-2] (yesterday settle).
                # If no today bar yet → use iloc[-1] (last bar = yesterday settle).
                import pytz as _pytz
                from datetime import datetime as _dt
                hist_f = t.history(period="5d", interval="1d", auto_adjust=True)
                hist_f = hist_f.dropna(subset=["Close"])
                if len(hist_f) >= 2:
                    try:
                        price = float(fi.last_price)
                    except Exception:
                        price = float(hist_f["Close"].iloc[-1])
                    _et = _pytz.timezone("America/New_York")
                    _today_et = _dt.now(_et).date()
                    _last_bar_date = hist_f.index[-1].date()
                    if _last_bar_date >= _today_et:
                        # In-progress today bar exists → yesterday's settle
                        prev_settle = float(hist_f["Close"].iloc[-2])
                    else:
                        # No today bar yet (pre-market) → last bar = yesterday settle
                        prev_settle = float(hist_f["Close"].iloc[-1])
                    if price > 0 and prev_settle > 0:
                        chg = (price - prev_settle) / prev_settle * 100
                    else:
                        price = None
            else:
                # Spot index / FX / commodity: compare last_price to previous_close
                price = float(fi.last_price)
                prev = float(fi.previous_close)
                if price > 0 and prev > 0:
                    chg = (price - prev) / prev * 100
                else:
                    price = None
        except Exception:
            price = None
        # Fallback: history close-to-close
        if price is None:
            try:
                hist = yf.Ticker(sym).history(period="5d", interval="1d", auto_adjust=True)
                hist = hist.dropna(subset=["Close"])
                if len(hist) >= 2:
                    price = float(hist["Close"].iloc[-1])
                    prev  = float(hist["Close"].iloc[-2])
                    chg   = (price - prev) / prev * 100
            except Exception:
                pass
        out.append((label, price, chg, kind, row))
    return out

def _mkt_tile(label, price, chg, kind):
    if price is None:
        return (f"<div style='padding:10px 14px;background:#f9fafb;border-radius:10px;"
                f"border:1px solid #e5e7eb;min-width:110px'>"
                f"<div style='font-size:11px;color:#9ca3af'>{label}</div>"
                f"<div style='font-size:13px;color:#d1d5db'>—</div></div>")

    color = "#16a34a" if chg >= 0 else "#dc2626"
    arrow = "▲" if chg >= 0 else "▼"
    sign  = "+" if chg >= 0 else ""

    if kind == "idx":
        p_str = f"{price:,.0f}"
    elif kind == "fx":
        p_str = f"₹{price:.2f}"
    elif kind == "vix":
        p_str = f"{price:.2f}"
    else:
        p_str = f"${price:,.1f}"

    return (f"<div style='padding:10px 14px;background:#f9fafb;border-radius:10px;"
            f"border:1px solid #e5e7eb;min-width:110px;flex:1'>"
            f"<div style='font-size:11px;color:#1e40af;font-weight:700;margin-bottom:4px;letter-spacing:0.2px'>{label}</div>"
            f"<div style='font-size:15px;font-weight:700;color:#111'>{p_str}</div>"
            f"<div style='font-size:11px;font-weight:600;color:{color};margin-top:2px'>"
            f"{arrow} {sign}{chg:.2f}%</div></div>")

_mkt_data = _fetch_markets()
_tiles_row1 = "".join(_mkt_tile(l, p, c, k) for l, p, c, k, r in _mkt_data if r == 1)
_tiles_row2 = "".join(_mkt_tile(l, p, c, k) for l, p, c, k, r in _mkt_data if r == 2)
_tiles_row3 = "".join(_mkt_tile(l, p, c, k) for l, p, c, k, r in _mkt_data if r == 3)
_tiles_row4 = "".join(_mkt_tile(l, p, c, k) for l, p, c, k, r in _mkt_data if r == 4)

# FII/DII tiles — fetched here so they appear inline with market tiles
@st.cache_data(ttl=1800, show_spinner=False)
def _fetch_fii_dii():
    import requests
    try:
        hdrs = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
            "Referer":    "https://www.nseindia.com",
            "Accept":     "application/json, text/plain, */*",
        }
        s = requests.Session()
        s.get("https://www.nseindia.com", headers=hdrs, timeout=8)
        r = s.get("https://www.nseindia.com/api/fiidiiTradeReact", headers=hdrs, timeout=8)
        data = r.json()
        fii = dii = None
        for row in data:
            cat = str(row.get("category", "")).upper()
            net = row.get("netPurchaseSales") or row.get("netValue") or row.get("net") or 0
            try:
                net = float(str(net).replace(",", ""))
            except Exception:
                net = 0
            if "FII" in cat or "FPI" in cat:
                fii = net
            elif "DII" in cat:
                dii = net
        return fii, dii
    except Exception:
        return None, None

@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_pcr():
    """Compute Nifty PCR from NSE FO bhavcopy (daily archive)."""
    import requests, io, zipfile
    import pandas as pd
    from datetime import date, timedelta
    today = date.today()
    for offset in range(0, 5):
        d = today - timedelta(days=offset)
        if d.weekday() >= 5:
            continue
        url = (f"https://archives.nseindia.com/content/fo/"
               f"BhavCopy_NSE_FO_0_0_0_{d.strftime('%Y%m%d')}_F_0000.csv.zip")
        try:
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            if r.status_code != 200 or len(r.content) < 1000:
                continue
            z = zipfile.ZipFile(io.BytesIO(r.content))
            df = pd.read_csv(z.open(z.namelist()[0]))
            nifty = df[df["TckrSymb"] == "NIFTY"]
            ce_oi = float(nifty[nifty["OptnTp"] == "CE"]["OpnIntrst"].sum())
            pe_oi = float(nifty[nifty["OptnTp"] == "PE"]["OpnIntrst"].sum())
            if ce_oi <= 0:
                continue
            return round(pe_oi / ce_oi, 3), ce_oi, pe_oi
        except Exception:
            continue
    return None, None, None


@st.cache_data(ttl=900, show_spinner=False)
def _fetch_breadth():
    import yfinance as yf
    nifty50 = [
        "RELIANCE.NS","TCS.NS","HDFCBANK.NS","ICICIBANK.NS","BHARTIARTL.NS",
        "INFY.NS","KOTAKBANK.NS","LT.NS","HINDUNILVR.NS","ITC.NS",
        "SBIN.NS","AXISBANK.NS","BAJFINANCE.NS","ASIANPAINT.NS","MARUTI.NS",
        "ULTRACEMCO.NS","TITAN.NS","NESTLEIND.NS","WIPRO.NS","BAJAJFINSV.NS",
        "M&M.NS","SUNPHARMA.NS","TECHM.NS","NTPC.NS","POWERGRID.NS",
        "TATAMOTORS.NS","TATASTEEL.NS","HCLTECH.NS","INDUSINDBK.NS","JSWSTEEL.NS",
        "ADANIPORTS.NS","ONGC.NS","COALINDIA.NS","ADANIENT.NS","GRASIM.NS",
        "DRREDDY.NS","HEROMOTOCO.NS","BAJAJ-AUTO.NS","BRITANNIA.NS","BPCL.NS",
        "EICHERMOT.NS","HINDALCO.NS","SHRIRAMFIN.NS","TATACONSUM.NS","CIPLA.NS",
        "APOLLOHOSP.NS","LTIM.NS","SBILIFE.NS","HDFCLIFE.NS","DIVISLAB.NS",
    ]
    try:
        raw = yf.download(nifty50, period="2d", auto_adjust=True, progress=False)
        close = raw["Close"].dropna(how="all")
        if len(close) < 2:
            return None, None, None
        chg = close.iloc[-1] / close.iloc[-2] - 1
        adv = int((chg >  0.001).sum())
        dec = int((chg < -0.001).sum())
        unc = int(((chg >= -0.001) & (chg <= 0.001)).sum())
        return adv, dec, unc
    except Exception:
        return None, None, None

def _fii_tile(label, val):
    if val is None:
        return (f"<div style='padding:10px 14px;background:#f9fafb;border-radius:10px;"
                f"border:1px solid #e5e7eb;min-width:110px;flex:1'>"
                f"<div style='font-size:11px;color:#1e40af;font-weight:700;margin-bottom:4px;letter-spacing:0.2px'>{label}</div>"
                f"<div style='font-size:15px;font-weight:700;color:#d1d5db'>—</div>"
                f"<div style='font-size:11px;color:#d1d5db;margin-top:2px'>No data</div></div>")
    color = "#16a34a" if val >= 0 else "#dc2626"
    arrow = "▲" if val >= 0 else "▼"
    sign  = "+" if val >= 0 else ""
    abs_cr = abs(val)
    p_str = f"₹{abs_cr/100:.1f}K Cr" if abs_cr >= 100000 else f"₹{abs_cr:,.0f} Cr"
    status = "Net Buy" if val >= 0 else "Net Sell"
    return (f"<div style='padding:10px 14px;background:#f9fafb;border-radius:10px;"
            f"border:1px solid #e5e7eb;min-width:110px;flex:1'>"
            f"<div style='font-size:11px;color:#1e40af;font-weight:700;margin-bottom:4px;letter-spacing:0.2px'>{label}</div>"
            f"<div style='font-size:15px;font-weight:700;color:#111'>{sign}{p_str}</div>"
            f"<div style='font-size:11px;font-weight:600;color:{color};margin-top:2px'>{arrow} {status}</div></div>")


def _pcr_tile(pcr, ce_oi, pe_oi):
    if pcr is None:
        return (f"<div style='padding:10px 14px;background:#f9fafb;border-radius:10px;"
                f"border:1px solid #e5e7eb;min-width:110px;flex:1'>"
                f"<div style='font-size:11px;color:#1e40af;font-weight:700;margin-bottom:4px;letter-spacing:0.2px'>📉 Nifty PCR</div>"
                f"<div style='font-size:15px;font-weight:700;color:#d1d5db'>—</div>"
                f"<div style='font-size:11px;color:#d1d5db;margin-top:2px'>Unavailable</div></div>")
    if pcr >= 1.3:
        label, color, icon = "Oversold", "#16a34a", "🐻"
    elif pcr >= 1.0:
        label, color, icon = "Neutral–Bearish", "#f59e0b", "⚖"
    elif pcr >= 0.8:
        label, color, icon = "Neutral–Bullish", "#f59e0b", "⚖"
    else:
        label, color, icon = "Overbought", "#dc2626", "🐂"
    return (f"<div style='padding:10px 14px;background:#f9fafb;border-radius:10px;"
            f"border:1px solid #e5e7eb;min-width:110px;flex:1'>"
            f"<div style='font-size:11px;color:#1e40af;font-weight:700;margin-bottom:4px;letter-spacing:0.2px'>📉 Nifty PCR</div>"
            f"<div style='font-size:15px;font-weight:700;color:#111'>{pcr:.3f}</div>"
            f"<div style='font-size:11px;font-weight:600;color:{color};margin-top:2px'>{icon} {label}</div></div>")

_fii_net, _dii_net = _fetch_fii_dii()
_pcr_val, _pcr_ce, _pcr_pe = _fetch_pcr()
_fii_tiles_html = (_fii_tile("🏦 FII / FPI", _fii_net)
                   + _fii_tile("🏦 DII", _dii_net)
                   + _pcr_tile(_pcr_val, _pcr_ce, _pcr_pe))

# ── Nifty 50 Signal (fetched early — used in tiles row) ──────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def _fetch_nifty_signal():
    import yfinance as yf
    hist = yf.Ticker("^NSEI").history(period="120d", interval="1d", auto_adjust=True)
    hist = hist.dropna(subset=["Close"])
    close = hist["Close"]
    high  = hist["High"]
    low   = hist["Low"]
    open_ = hist["Open"]
    ema9  = close.ewm(span=9,  adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    ema50 = close.ewm(span=50, adjust=False).mean()
    delta = close.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    rsi   = 100 - 100 / (1 + gain / loss)
    c, e9, e21, e50 = float(close.iloc[-1]), float(ema9.iloc[-1]), float(ema21.iloc[-1]), float(ema50.iloc[-1])
    r = float(rsi.iloc[-1])
    if e9 > e21 > e50 and c > e9 and r > 50:
        signal = "BUY"
    elif e9 < e21 and e21 < e50 and c < e21 and r < 50:
        signal = "SELL"
    else:
        signal = "NEUTRAL"
    n = 40
    vol    = hist["Volume"].fillna(0)
    avg_v  = vol.rolling(20).mean().fillna(vol)
    last_v = float(vol.iloc[-1])
    last_avg = float(avg_v.iloc[-1])
    rvol_last = round(last_v / last_avg, 1) if last_avg > 0 else 1.0
    return {
        "signal": signal, "price": c,
        "ema9": e9, "ema21": e21, "ema50": e50, "rsi": r,
        "rvol_last": rvol_last,
        "dates":   list(hist.index[-n:]),
        "open":    list(open_.iloc[-n:].round(0)),
        "high":    list(high.iloc[-n:].round(0)),
        "low":     list(low.iloc[-n:].round(0)),
        "close":   list(close.iloc[-n:].round(0)),
        "ema9s":   list(ema9.iloc[-n:].round(1)),
        "ema21s":  list(ema21.iloc[-n:].round(1)),
        "ema50s":  list(ema50.iloc[-n:].round(1)),
        "volume":  list(vol.iloc[-n:].astype(int)),
        "avg_vol": list(avg_v.iloc[-n:].astype(int)),
    }

_nifty_data = _fetch_nifty_signal()

_tiles_left, _tiles_right = st.columns([1.7, 1])

with _tiles_left:
    st.markdown(
        f"<div style='display:flex;gap:8px;flex-wrap:nowrap;margin-bottom:6px'>{_tiles_row1}</div>"
        f"<div style='display:flex;gap:8px;flex-wrap:nowrap;margin-bottom:6px'>{_tiles_row2}</div>"
        f"<div style='display:flex;gap:8px;flex-wrap:nowrap;margin-bottom:6px'>{_tiles_row3}</div>"
        f"<div style='display:flex;gap:8px;flex-wrap:nowrap;margin-bottom:6px'>{_tiles_row4}{_fii_tiles_html}</div>",
        unsafe_allow_html=True,
    )
    st.caption("Global markets · FII/DII · Nifty PCR · refreshed every 15–60 min")

with _tiles_right:
    _nd  = _nifty_data
    _sig = _nd["signal"]
    _sc  = "#16a34a" if _sig == "BUY" else ("#dc2626" if _sig == "SELL" else "#f59e0b")
    st.markdown(
        f"<div style='font-size:12px;font-weight:700;color:#1e40af;margin-bottom:2px'>📊 Nifty 50 · Daily Signal</div>"
        f"<div style='font-size:18px;font-weight:800;color:{_sc};margin-bottom:2px'>"
        f"{'▲' if _sig=='BUY' else ('▼' if _sig=='SELL' else '●')} {_sig}"
        f"<span style='font-size:12px;font-weight:400;color:#6b7280;margin-left:10px'>"
        f"₹{_nd['price']:,.0f} · RSI {_nd['rsi']:.0f}</span></div>",
        unsafe_allow_html=True,
    )
    # Taller chart to fill the tile area height
    def _nifty_chart_compact(d):
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        sig       = d["signal"]
        sig_color = "#16a34a" if sig == "BUY" else ("#dc2626" if sig == "SELL" else "#f59e0b")
        bg_fill   = ("rgba(22,163,74,0.05)" if sig == "BUY"
                     else "rgba(220,38,38,0.05)" if sig == "SELL"
                     else "rgba(245,158,11,0.05)")
        fig = make_subplots(rows=2, cols=1, row_heights=[0.70, 0.30],
                            shared_xaxes=True, vertical_spacing=0.02)
        fig.add_shape(type="rect", xref="paper", yref="paper",
                      x0=0, x1=1, y0=0.30, y1=1,
                      fillcolor=bg_fill, line_width=0, layer="below")
        fig.add_trace(go.Candlestick(
            x=d["dates"], open=d["open"], high=d["high"], low=d["low"], close=d["close"],
            increasing_line_color="#16a34a", increasing_fillcolor="#16a34a",
            decreasing_line_color="#dc2626", decreasing_fillcolor="#dc2626",
            name="Nifty", showlegend=False,
        ), row=1, col=1)
        fig.add_trace(go.Scatter(x=d["dates"], y=d["ema9s"],
            line=dict(color="#3b82f6", width=1.2), name="EMA9", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=d["dates"], y=d["ema21s"],
            line=dict(color="#f59e0b", width=1.2), name="EMA21", showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=d["dates"], y=d["ema50s"],
            line=dict(color="#8b5cf6", width=1.5), name="EMA50", showlegend=False), row=1, col=1)
        fig.add_hline(y=d["price"], line_dash="dot", line_color="#374151", line_width=1,
                      annotation_text=f"₹{d['price']:,.0f}",
                      annotation_position="right",
                      annotation_font=dict(size=9, color="#374151"), row=1, col=1)
        # Volume bars
        vol_colors = []
        for i in range(len(d["close"])):
            up = d["close"][i] >= d["open"][i]
            above = d["volume"][i] > d["avg_vol"][i]
            vol_colors.append(("#16a34a" if above else "#86efac") if up else ("#dc2626" if above else "#fca5a5"))
        fig.add_trace(go.Bar(x=d["dates"], y=d["volume"], marker_color=vol_colors,
                             showlegend=False, hovertemplate="Vol: %{y:,}<extra></extra>"), row=2, col=1)
        fig.add_trace(go.Scatter(x=d["dates"], y=d["avg_vol"],
            line=dict(color="#9ca3af", width=1, dash="dash"),
            showlegend=False), row=2, col=1)
        rvol = d["rvol_last"]
        rv_c = "#16a34a" if rvol >= 1.5 else ("#f59e0b" if rvol >= 1.0 else "#9ca3af")
        fig.add_annotation(xref="paper", yref="y2", x=0.99, y=max(d["volume"][-5:]),
            text=f"<b>{rvol}×</b>", showarrow=False,
            font=dict(size=9, color=rv_c), xanchor="right", yanchor="bottom")
        fig.update_layout(
            height=320,
            margin=dict(t=4, b=16, l=50, r=55),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#fafafa",
            xaxis=dict(showgrid=False, tickfont=dict(size=8), tickformat="%d %b"),
            xaxis2=dict(showgrid=False, rangeslider=dict(visible=False),
                        tickfont=dict(size=8), tickformat="%d %b"),
            yaxis=dict(showgrid=True, gridcolor="#eeeeee", tickfont=dict(size=8), tickformat=",.0f"),
            yaxis2=dict(showgrid=False, tickfont=dict(size=7), tickformat=".2s"),
            hovermode="x unified", bargap=0.15,
        )
        return fig
    st.plotly_chart(_nifty_chart_compact(_nd), use_container_width=True,
                    config={"displayModeBar": False})

# ── FII/DII + Market Breadth + F&O Expiry ────────────────────────────────────
import calendar as _cal
from datetime import date as _date

def _next_fo_expiry():
    from datetime import timedelta as _td
    today = _date.today()

    def last_weekday_of_month(y, m, wd):
        last = _cal.monthrange(y, m)[1]
        for d in range(last, 0, -1):
            if _date(y, m, d).weekday() == wd:
                return _date(y, m, d)

    def next_weekday(wd):  # 0=Mon…6=Sun; returns next occurrence (not today)
        days = (wd - today.weekday()) % 7
        if days == 0:
            days = 7
        return today + _td(days=days)

    # NSE Monthly expiry — last Thursday of current (or next) month
    exp = last_weekday_of_month(today.year, today.month, 3)
    if exp <= today:
        nm = today.month % 12 + 1
        ny = today.year + (1 if today.month == 12 else 0)
        exp = last_weekday_of_month(ny, nm, 3)

    # BSE/Sensex Monthly expiry — last Friday of current (or next) month
    bse_exp = last_weekday_of_month(today.year, today.month, 4)
    if bse_exp <= today:
        nm = today.month % 12 + 1
        ny = today.year + (1 if today.month == 12 else 0)
        bse_exp = last_weekday_of_month(ny, nm, 4)

    weekly = [
        ("Midcap Nifty", next_weekday(0)),   # Monday
        ("Fin Nifty",    next_weekday(1)),   # Tuesday
        ("Bank Nifty",   next_weekday(2)),   # Wednesday
        ("Nifty 50",     next_weekday(3)),   # Thursday
        ("Sensex",       next_weekday(4)),   # Friday (BSE)
    ]
    return exp, (exp - today).days, bse_exp, (bse_exp - today).days, weekly

_exp_date, _exp_days, _bse_exp_date, _bse_exp_days, _weekly_expiries = _next_fo_expiry()

st.markdown("---")

# ── Fear & Greed Index ────────────────────────────────────────────────────────
@st.cache_data(ttl=86400, show_spinner=False)
def _calc_fear_greed():
    """5-signal composite Fear & Greed for NSE. Cached 24h."""
    import yfinance as yf

    scores  = {}
    signals = {}

    try:
        hist  = yf.Ticker("^NSEI").history(period="2y")
        close = hist["Close"].dropna()
        price = float(close.iloc[-1])

        # Signal 1: Long-term momentum — price vs 125d SMA
        # +8% above SMA → 100 (extreme greed), -8% below → 0 (extreme fear)
        if len(close) >= 125:
            sma125 = float(close.rolling(125).mean().iloc[-1])
            pct125 = (price - sma125) / sma125 * 100
            s1 = max(0.0, min(100.0, 50 + pct125 * 6.25))
            scores["momentum_long"] = s1
            signals["Long Momentum"] = (s1, f"{'▲' if pct125>=0 else '▼'} {abs(pct125):.1f}% vs 125d SMA")

        # Signal 2: Short-term momentum — price vs 20d SMA
        # +5% above SMA → 100, -5% below → 0
        if len(close) >= 20:
            sma20 = float(close.rolling(20).mean().iloc[-1])
            pct20 = (price - sma20) / sma20 * 100
            s2 = max(0.0, min(100.0, 50 + pct20 * 10))
            scores["momentum_short"] = s2
            signals["Short Momentum"] = (s2, f"{'▲' if pct20>=0 else '▼'} {abs(pct20):.1f}% vs 20d SMA")

        # Signal 3: RSI (14-day) — re-scaled so 30=0, 70=100
        # RSI naturally ranges 30-70 in trending markets; map that to 0-100
        if len(close) >= 15:
            delta = close.diff()
            gain  = delta.clip(lower=0).rolling(14).mean()
            loss  = (-delta.clip(upper=0)).rolling(14).mean()
            rsi   = float((100 - 100 / (1 + gain / loss)).iloc[-1])
            s3 = max(0.0, min(100.0, (rsi - 30) / 40 * 100))
            scores["rsi"] = s3
            signals["RSI (14d)"] = (s3, f"{rsi:.1f}")

        # Signal 4: 52-week high proximity
        # Within 2% of 52W high → 90+, 20%+ below → 0
        if len(close) >= 252:
            high52 = float(close.rolling(252).max().iloc[-1])
            pct_from_high = (price - high52) / high52 * 100   # negative
            s4 = max(0.0, min(100.0, 100 + pct_from_high * 5))
            scores["high52"] = s4
            signals["52W High Prox."] = (s4, f"{pct_from_high:.1f}% from high")

    except Exception:
        pass

    try:
        # Signal 5: India VIX inverse — low VIX = calm = greed
        # VIX ≤ 12 → 100, VIX ≥ 28 → 0  (realistic India VIX range)
        vix_hist = yf.Ticker("^INDIAVIX").history(period="5d")
        if not vix_hist.empty:
            vix_val = float(vix_hist["Close"].dropna().iloc[-1])
            s5 = max(0.0, min(100.0, (28 - vix_val) / 16 * 100))
            scores["vix"] = s5
            signals["India VIX"] = (s5, f"{vix_val:.2f}")
    except Exception:
        pass

    if not scores:
        return None, "Unavailable", "#9ca3af", {}

    composite = sum(scores.values()) / len(scores)

    if composite >= 75:
        label, color = "Extreme Greed", "#16a34a"
    elif composite >= 55:
        label, color = "Greed", "#4ade80"
    elif composite >= 45:
        label, color = "Neutral", "#f59e0b"
    elif composite >= 25:
        label, color = "Fear", "#f97316"
    else:
        label, color = "Extreme Fear", "#dc2626"

    return round(composite), label, color, signals


def _gauge_fig(value, label, color):
    import plotly.graph_objects as go
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": f"<b>{label}</b>", "font": {"size": 13, "color": "#374151"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#9ca3af",
                "tickvals": [0, 25, 45, 55, 75, 100],
                "ticktext": ["0", "25", "45", "55", "75", "100"],
            },
            "bar": {"color": "#1e293b", "thickness": 0.25},
            "bgcolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
            "steps": [
                {"range": [0,  25],  "color": "#fca5a5"},
                {"range": [25, 45],  "color": "#fdba74"},
                {"range": [45, 55],  "color": "#fde047"},
                {"range": [55, 75],  "color": "#86efac"},
                {"range": [75, 100], "color": "#4ade80"},
            ],
            "threshold": {
                "line": {"color": "#1e293b", "width": 4},
                "thickness": 0.8,
                "value": value,
            },
        },
        number={"font": {"size": 26, "color": color}},
    ))
    fig.update_layout(
        height=185,
        margin={"t": 50, "b": 0, "l": 20, "r": 20},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )
    return fig


_fg_val, _fg_label, _fg_color, _fg_signals = _calc_fear_greed()

# ── Top Sectors (1W) ──────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_top_sectors():
    import yfinance as yf
    sectors = [
        ("IT",        "^CNXIT"),
        ("Bank",      "^NSEBANK"),
        ("Auto",      "^CNXAUTO"),
        ("Pharma",    "^CNXPHARMA"),
        ("FMCG",      "^CNXFMCG"),
        ("Metal",     "^CNXMETAL"),
        ("Realty",    "^CNXREALTY"),
        ("Energy",    "^CNXENERGY"),
        ("Infra",     "^CNXINFRA"),
        ("Media",     "^CNXMEDIA"),
        ("PSU Bank",  "^CNXPSUBANK"),
        ("Finance",   "^CNXFIN"),
        ("MNC",       "^CNXMNC"),
        ("Consumption","^CNXCONSUM"),
    ]
    results = []
    for name, sym in sectors:
        try:
            hist  = yf.Ticker(sym).history(period="10d")
            close = hist["Close"].dropna()
            if len(close) >= 5:
                chg = (close.iloc[-1] - close.iloc[-5]) / close.iloc[-5] * 100
                results.append((name, round(chg, 2)))
        except Exception:
            pass
    results.sort(key=lambda x: x[1], reverse=True)
    return results

_sectors = _fetch_top_sectors()

# ── Fear & Greed  |  Top Sectors ─────────────────────────────────────────────
_fg_col, _gap1, _sec_col = st.columns([1, 0.05, 1.2])

with _fg_col:
    st.markdown("##### 😨 NSE Fear & Greed Index")
    if _fg_val is not None:
        st.plotly_chart(_gauge_fig(_fg_val, _fg_label, _fg_color),
                        use_container_width=True, config={"displayModeBar": False})

        # Signal breakdown pills
        _sig_zone = {
            (75, 101): ("Extreme Greed", "#16a34a"),
            (55,  75): ("Greed",         "#4ade80"),
            (45,  55): ("Neutral",       "#f59e0b"),
            (25,  45): ("Fear",          "#f97316"),
            (0,   25): ("Extreme Fear",  "#dc2626"),
        }
        def _zone(v):
            for (lo, hi), (lbl, clr) in _sig_zone.items():
                if lo <= v < hi:
                    return lbl, clr
            return "Neutral", "#f59e0b"

        _pills = ""
        for sig_name, (sig_val, sig_detail) in _fg_signals.items():
            zlbl, zclr = _zone(sig_val)
            _pills += (
                f"<div style='display:flex;justify-content:space-between;"
                f"align-items:center;padding:2px 0;border-bottom:1px solid #f3f4f6'>"
                f"<span style='font-size:11px;color:#6b7280'>{sig_name}</span>"
                f"<span style='font-size:10px;font-weight:600;color:{zclr};"
                f"background:{zclr}18;padding:1px 6px;border-radius:99px'>{zlbl}</span>"
                f"<span style='font-size:10px;color:#9ca3af;min-width:70px;text-align:right'>{sig_detail}</span>"
                f"</div>"
            )
        st.markdown(
            f"<div style='padding:2px 0'>{_pills}</div>"
            f"<div style='font-size:10px;color:#d1d5db;margin-top:4px'>Updated daily · 5 signals: momentum (long + short) · RSI · 52W high · India VIX</div>",
            unsafe_allow_html=True,
        )
    else:
        st.info("Market data unavailable")

with _sec_col:
    st.markdown("##### 🏭 Top Sectors · 1W")
    if _sectors:
        top5    = _sectors[:5]
        bottom3 = _sectors[-3:]
        _rows = ""
        for i, (name, chg) in enumerate(top5):
            color = "#16a34a"
            bar_w = min(100, int(abs(chg) * 8))
            _rows += (
                f"<div style='display:flex;align-items:center;gap:8px;"
                f"padding:5px 0;border-bottom:1px solid #f3f4f6'>"
                f"<span style='font-size:12px;font-weight:700;color:#9ca3af;width:14px'>{i+1}</span>"
                f"<span style='font-size:12px;color:#111;flex:1'>{name}</span>"
                f"<div style='flex:1;background:#f3f4f6;border-radius:4px;height:6px'>"
                f"<div style='width:{bar_w}%;background:{color};border-radius:4px;height:6px'></div></div>"
                f"<span style='font-size:12px;font-weight:700;color:{color};min-width:52px;text-align:right'>"
                f"+{chg:.2f}%</span>"
                f"</div>"
            )
        st.markdown(f"<div style='margin-bottom:10px'>{_rows}</div>", unsafe_allow_html=True)

        st.markdown("<div style='font-size:11px;color:#9ca3af;font-weight:600;margin:6px 0 2px'>Bottom 3</div>",
                    unsafe_allow_html=True)
        _bot = ""
        for name, chg in bottom3:
            color = "#dc2626" if chg < 0 else "#6b7280"
            sign  = "+" if chg >= 0 else ""
            _bot += (
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:3px 0;border-bottom:1px solid #f3f4f6'>"
                f"<span style='font-size:11px;color:#6b7280'>{name}</span>"
                f"<span style='font-size:11px;font-weight:700;color:{color}'>{sign}{chg:.2f}%</span>"
                f"</div>"
            )
        st.markdown(f"<div>{_bot}</div>"
                    f"<div style='font-size:10px;color:#d1d5db;margin-top:8px'>NSE sector indices · refreshed 1h</div>",
                    unsafe_allow_html=True)
    else:
        st.info("Sector data unavailable")

st.markdown("---")

# ── Dashboards ────────────────────────────────────────────────────────────────
st.markdown("##### 🗂 Dashboards")
_pc1, _pc2, _pc3 = st.columns(3)

with _pc1:
    st.markdown("""
    **📊 Analysis**
    NSE F&O Screener
    - Probable Upside
    - Support Entry
    - Consolidation
    - Backtest · F&O list

    👈 Click **Analysis**
    """)

with _pc2:
    st.markdown("""
    **🚀 Project Up**
    NSE Equity Screener
    - Full NSE (~2200 stocks)
    - 10-signal PVA model
    - Top 15 setups
    - Backtest

    👈 Click **Project Up**
    """)

with _pc3:
    st.markdown("""
    **📈 Trading Setup**
    Short-Term Dashboard
    - EMA/RSI/ADX/VWAP
    - Candlestick + BB chart
    - Backtest SL/TP
    - Stock Scanner

    👈 Click **Trading Setup**
    """)

st.markdown("---")

# ── F&O Expiry ────────────────────────────────────────────────────────────────
st.markdown("##### 📅 F&O Expiry")
today_d = _date.today()

_wrows = ""
for name, exp in _weekly_expiries:
    days = (exp - today_d).days
    color = "#dc2626" if days <= 1 else ("#f59e0b" if days <= 3 else "#374151")
    badge = (f"<span style='font-size:10px;background:#fee2e2;color:#dc2626;padding:1px 6px;border-radius:99px;margin-left:4px'>Tomorrow</span>" if days == 1 else
             f"<span style='font-size:10px;background:#fef9c3;color:#b45309;padding:1px 6px;border-radius:99px;margin-left:4px'>This week</span>" if days <= 4 else "")
    _wrows += (
        f"<div style='display:inline-flex;align-items:center;gap:6px;padding:5px 14px;"
        f"border:1px solid #e5e7eb;border-radius:8px;margin:4px 4px 4px 0'>"
        f"<span style='font-size:12px;color:#374151;font-weight:600'>{name}</span>"
        f"<span style='font-size:11px;color:#6b7280'>{exp.strftime('%d %b')}</span>"
        f"<span style='font-size:12px;font-weight:700;color:{color}'>{days}d</span>"
        f"{badge}</div>"
    )

def _m_row(label, exp_d, days):
    color = "#dc2626" if days <= 3 else ("#f59e0b" if days <= 7 else "#16a34a")
    return (
        f"<div style='display:inline-flex;align-items:center;gap:6px;padding:5px 14px;"
        f"border:1px solid #e5e7eb;border-radius:8px;margin:4px 4px 4px 0'>"
        f"<span style='font-size:12px;color:#374151;font-weight:600'>{label}</span>"
        f"<span style='font-size:11px;color:#6b7280'>{exp_d.strftime('%d %b')}</span>"
        f"<span style='font-size:13px;font-weight:800;color:{color}'>{days}d</span>"
        f"</div>"
    )

st.markdown(
    f"<div style='font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px'>Weekly</div>"
    f"<div style='display:flex;flex-wrap:wrap'>{_wrows}</div>"
    f"<div style='font-size:11px;font-weight:700;color:#9ca3af;text-transform:uppercase;letter-spacing:.5px;margin:10px 0 4px'>Monthly</div>"
    f"<div style='display:flex;flex-wrap:wrap'>"
    + _m_row("NSE · Nifty / BankNifty / Stocks", _exp_date, _exp_days)
    + _m_row("BSE · Sensex / Bankex", _bse_exp_date, _bse_exp_days) +
    f"</div>"
    f"<div style='font-size:10px;color:#d1d5db;margin-top:8px'>NSE = last Thu · BSE = last Fri of month</div>",
    unsafe_allow_html=True,
)

# ── Nifty 50 Breadth ──────────────────────────────────────────────────────────
_adv, _dec, _unc = _fetch_breadth()
if _adv is not None:
    total = _adv + _dec + (_unc or 0)
    adv_pct = _adv / total * 100 if total else 0
    dec_pct = _dec / total * 100 if total else 0
    mood = "Bullish" if _adv > _dec * 1.5 else ("Bearish" if _dec > _adv * 1.5 else "Mixed")
    mood_color = "#16a34a" if mood == "Bullish" else ("#dc2626" if mood == "Bearish" else "#f59e0b")
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:10px;padding:6px 0'>"
        f"<span style='font-size:11px;font-weight:700;color:#6b7280'>📊 Nifty 50 Breadth</span>"
        f"<span style='font-size:12px;font-weight:700;color:{mood_color};"
        f"background:{mood_color}18;padding:1px 8px;border-radius:99px'>{mood}</span>"
        f"<span style='font-size:14px;font-weight:800;color:#16a34a'>{_adv}<span style='font-size:10px;font-weight:400;color:#6b7280'> Adv</span></span>"
        f"<span style='font-size:14px;font-weight:800;color:#dc2626'>{_dec}<span style='font-size:10px;font-weight:400;color:#6b7280'> Dec</span></span>"
        f"<span style='font-size:14px;font-weight:800;color:#9ca3af'>{_unc}<span style='font-size:10px;font-weight:400;color:#6b7280'> Unch</span></span>"
        f"<div style='flex:1;background:#f3f4f6;border-radius:4px;height:5px;overflow:hidden;max-width:400px'>"
        f"<div style='display:flex;height:100%'>"
        f"<div style='width:{adv_pct:.0f}%;background:#16a34a'></div>"
        f"<div style='width:{dec_pct:.0f}%;background:#dc2626'></div>"
        f"</div></div></div>",
        unsafe_allow_html=True,
    )

st.caption("Use the sidebar navigation to switch between dashboards.")
