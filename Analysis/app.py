import streamlit as st
import pandas as pd

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NSE F&O Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — Dashboard Theme ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Base ── */
html, body, [data-testid="stAppViewContainer"], .main {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.main { background: #f1f5f9 !important; }
.main .block-container {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}

/* ── Remove Streamlit top header bar ── */
[data-testid="stHeader"] { display: none !important; height: 0 !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
header { display: none !important; height: 0 !important; }
:root { --header-height: 0rem !important; }

/* ── Kill all top padding/margin on every container layer ── */
section.main > div { padding-top: 0 !important; margin-top: 0 !important; }
.appview-container .main .block-container { padding-top: 0 !important; }
[data-testid="stMainBlockContainer"] { padding-top: 0 !important; }
div.block-container { padding-top: 0 !important; margin-top: 0 !important; }
.stApp > div:first-child { padding-top: 0 !important; margin-top: 0 !important; }

/* ── Pull navbar flush to top ── */
.top-navbar { margin-top: -2rem !important; }

/* ── Tighten vertical spacing between elements ── */
[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stVerticalBlock"] > div { gap: 0 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #f1f5f9 !important; }
[data-testid="stSidebar"] input {
    background: #1e293b !important;
    border: 1px solid #334155 !important;
    color: #f1f5f9 !important;
    border-radius: 6px !important;
}
[data-testid="stSidebar"] details summary,
[data-testid="stSidebar"] details p { color: #94a3b8 !important; }

/* ── Top navbar ── */
.top-navbar {
    background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
    padding: 1.1rem 2.2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0;
}
.nav-title {
    font-size: 1.45rem;
    font-weight: 700;
    color: #f8fafc;
    letter-spacing: -0.02em;
    margin: 0;
}
.nav-subtitle {
    font-size: 0.78rem;
    color: #94a3b8;
    margin-top: 3px;
}
.nav-badge {
    background: #1d4ed8;
    color: #bfdbfe;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}

/* ── Content wrapper ── */
.content-wrap { padding: 0.6rem 2rem; }

/* ── Stat cards ── */
div[data-testid="metric-container"] {
    background: white;
    border-radius: 10px;
    padding: 1rem 1.2rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border-left: 4px solid #3b82f6;
}
div[data-testid="metric-container"] label { color: #64748b !important; font-size: 0.72rem !important; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 500 !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #0f172a !important; font-size: 1.4rem !important; font-weight: 700 !important; }

/* ── Section headers ── */
.section-header {
    background: #0f172a;
    padding: 0.85rem 1.4rem;
    border-radius: 10px 10px 0 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 0.5rem;
}
.section-header-title {
    color: #f8fafc;
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0;
    letter-spacing: -0.01em;
}
.section-badge {
    background: #1d4ed8;
    color: #bfdbfe;
    font-size: 0.7rem;
    padding: 3px 10px;
    border-radius: 12px;
    font-weight: 500;
}
.section-body {
    background: white;
    border-radius: 0 0 10px 10px;
    padding: 1.2rem 1.4rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}

/* ── Tables ── */
div[data-testid="stDataFrame"] {
    border-radius: 8px !important;
    overflow: hidden !important;
    border: 1px solid #e2e8f0 !important;
}

/* ── Buttons ── */
.stButton > button {
    background: #1d4ed8 !important;
    color: white !important;
    border: none !important;
    border-radius: 7px !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    padding: 0.45rem 1.2rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: #1e40af !important; }

/* ── Inputs ── */
.stTextInput input {
    border-radius: 7px !important;
    border: 1.5px solid #e2e8f0 !important;
    background: #f8fafc !important;
    font-size: 0.87rem !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    background: white !important;
}

/* ── Info / warning boxes ── */
div[data-testid="stInfo"] {
    background: #eff6ff !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 8px !important;
    color: #1e40af !important;
}
div[data-testid="stWarning"] {
    border-radius: 8px !important;
}

/* ── Caption ── */
.stCaption p { color: #64748b !important; font-size: 0.77rem !important; }

/* ── Progress bar ── */
div[data-testid="stProgressBar"] > div { background: #3b82f6 !important; }

/* ── Divider ── */
hr { border-color: #e2e8f0 !important; margin: 1.2rem 0 !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0.5rem 1rem; border-bottom:1px solid #1e293b; margin-bottom:1rem;">
        <div style="font-size:1.1rem;font-weight:700;color:#f8fafc;letter-spacing:-0.02em;">📊 F&amp;O Analysis</div>
        <div style="font-size:0.72rem;color:#64748b;margin-top:3px;">NSE Derivatives Screener</div>
    </div>
    """, unsafe_allow_html=True)

# ── Top Navbar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-navbar">
    <div>
        <div class="nav-title">📊 NSE F&amp;O Analysis</div>
        <div class="nav-subtitle">Futures &amp; Options Screener — <span style="font-size:0.72rem;opacity:0.7;">powered by yfinance</span></div>
    </div>
    <span class="nav-badge">NSE Live</span>
</div>
<div class="content-wrap" style="padding-bottom:0">
""", unsafe_allow_html=True)

# ── Company name lookup: NSE symbol → display name ───────────────────────────
_COMPANY_NAMES = {
    "ABB":"ABB India","POWERINDIA":"Hitachi Energy India","ADANIENT":"Adani Enterprises",
    "ADANIGREEN":"Adani Green Energy","ADANIPORTS":"Adani Ports & SEZ","ADANIPOWER":"Adani Power",
    "ADANIENSOL":"Adani Energy Solutions","ABCAPITAL":"Aditya Birla Capital","ALKEM":"Alkem Laboratories",
    "GVT&D":"GE Vernova T&D India","AMBUJACEM":"Ambuja Cements","AMBER":"Amber Enterprises India",
    "ANGELONE":"Angel One","APLAPOLLO":"APL Apollo Tubes","APOLLOHOSP":"Apollo Hospitals",
    "ASHOKLEY":"Ashok Leyland","ASIANPAINT":"Asian Paints","ASTRAL":"Astral",
    "AUROPHARMA":"Aurobindo Pharma","AUBANK":"AU Small Finance Bank","DMART":"Avenue Supermarts (D-Mart)",
    "AXISBANK":"Axis Bank","BAJAJ-AUTO":"Bajaj Auto","BAJAJFINSV":"Bajaj Finserv",
    "BAJFINANCE":"Bajaj Finance","BAJAJHLDNG":"Bajaj Holdings","BANDHANBNK":"Bandhan Bank",
    "BANKBARODA":"Bank of Baroda","BANKINDIA":"Bank of India","BHARTIARTL":"Bharti Airtel",
    "BDL":"Bharat Dynamics","BEL":"Bharat Electronics","BHARATFORG":"Bharat Forge",
    "INDUSTOWER":"Indus Towers","BPCL":"BPCL","BHEL":"BHEL","BIOCON":"Biocon",
    "BLUESTARCO":"Blue Star","BOSCHLTD":"Bosch India","BRITANNIA":"Britannia Industries",
    "BSE":"BSE","ZYDUSLIFE":"Zydus Lifesciences","CANBK":"Canara Bank","CDSL":"CDSL",
    "CHOLAFIN":"Cholamandalam Investment & Finance","CIPLA":"Cipla","COALINDIA":"Coal India",
    "COCHINSHIP":"Cochin Shipyard","COLPAL":"Colgate-Palmolive India","CAMS":"CAMS",
    "CONCOR":"Container Corp of India","CROMPTON":"Crompton Greaves Consumer","CGPOWER":"CG Power",
    "CUMMINSIND":"Cummins India","DABUR":"Dabur India","DELHIVERY":"Delhivery",
    "DIVISLAB":"Divi's Laboratories","DIXON":"Dixon Technologies","DLF":"DLF",
    "DRREDDY":"Dr. Reddy's Laboratories","EICHERMOT":"Eicher Motors","FEDERALBNK":"Federal Bank",
    "FORTIS":"Fortis Healthcare","FORCEMOT":"Force Motors","NYKAA":"Nykaa (FSN E-Commerce)",
    "GAIL":"GAIL India","GLENMARK":"Glenmark Pharmaceuticals","GMRAIRPORT":"GMR Airports",
    "GODREJCP":"Godrej Consumer Products","GODFRYPHLP":"Godfrey Phillips India",
    "GODREJPROP":"Godrej Properties","GRASIM":"Grasim Industries","HAVELLS":"Havells India",
    "HCLTECH":"HCL Technologies","HDFCAMC":"HDFC AMC","HDFCBANK":"HDFC Bank",
    "HDFCLIFE":"HDFC Life Insurance","HEROMOTOCO":"Hero MotoCorp","HAL":"Hindustan Aeronautics (HAL)",
    "HINDALCO":"Hindalco Industries","HINDUNILVR":"Hindustan Unilever","HINDPETRO":"HPCL",
    "HINDZINC":"Hindustan Zinc","HYUNDAI":"Hyundai Motor India","ICICIBANK":"ICICI Bank",
    "ICICIGI":"ICICI Lombard GI","ICICIPRULI":"ICICI Prudential Life","IDEA":"Vodafone Idea",
    "IDFCFIRSTB":"IDFC First Bank","360ONE":"360 ONE WAM","INDUSINDBK":"IndusInd Bank",
    "IEX":"Indian Energy Exchange","INDHOTEL":"Indian Hotels (Taj)","INDIANB":"Indian Bank",
    "IOC":"Indian Oil Corp","IRFC":"IRFC","IREDA":"IREDA","NAUKRI":"Info Edge (Naukri)",
    "INFY":"Infosys","INOXWIND":"INOX Wind","INDIGO":"IndiGo (InterGlobe Aviation)","ITC":"ITC",
    "JINDALSTEL":"Jindal Steel & Power","JIOFIN":"Jio Financial Services","JSWENERGY":"JSW Energy",
    "JSWSTEEL":"JSW Steel","JUBLFOOD":"Jubilant FoodWorks","KALYANKJIL":"Kalyan Jewellers",
    "KAYNES":"Kaynes Technology","KEI":"KEI Industries","KFINTECH":"KFin Technologies",
    "KOTAKBANK":"Kotak Mahindra Bank","KPITTECH":"KPIT Technologies","LT":"Larsen & Toubro",
    "LAURUSLABS":"Laurus Labs","LICI":"LIC India","LICHSGFIN":"LIC Housing Finance",
    "LTF":"L&T Finance","LTM":"LTIMindtree","LUPIN":"Lupin","LODHA":"Lodha Developers",
    "M&M":"Mahindra & Mahindra","MANAPPURAM":"Manappuram Finance","MANKIND":"Mankind Pharma",
    "MARICO":"Marico","MARUTI":"Maruti Suzuki","MFSL":"Max Financial Services",
    "MAXHEALTH":"Max Healthcare","MAZDOCK":"Mazagon Dock Shipbuilders","MCX":"MCX",
    "UNOMINDA":"UNO Minda","MOTILALOFS":"Motilal Oswal Financial Services",
    "MOTHERSON":"Motherson Sumi Systems","MPHASIS":"Mphasis","MUTHOOTFIN":"Muthoot Finance",
    "NATIONALUM":"National Aluminium","NMDC":"NMDC","NBCC":"NBCC India",
    "NESTLEIND":"Nestlé India","NHPC":"NHPC","COFORGE":"Coforge","NTPC":"NTPC",
    "OBEROIRLTY":"Oberoi Realty","DALBHARAT":"Dalmia Bharat","OIL":"Oil India",
    "PAYTM":"Paytm (One 97 Communications)","ONGC":"ONGC","OFSS":"Oracle Financial Services",
    "PAGEIND":"Page Industries","POLICYBZR":"PB Fintech (Policybazaar)",
    "PERSISTENT":"Persistent Systems","PETRONET":"Petronet LNG","PGEL":"PG Electroplast",
    "PHOENIXLTD":"Phoenix Mills","PIDILITIND":"Pidilite Industries","PIIND":"PI Industries",
    "PNBHOUSING":"PNB Housing Finance","POLYCAB":"Polycab India","PFC":"Power Finance Corp (PFC)",
    "POWERGRID":"Power Grid Corp","PREMIERENE":"Premier Energies","PRESTIGE":"Prestige Estates Projects",
    "PNB":"Punjab National Bank","RADICO":"Radico Khaitan","RVNL":"Rail Vikas Nigam (RVNL)",
    "RBLBANK":"RBL Bank","RELIANCE":"Reliance Industries","NAM-INDIA":"Nippon India AMC",
    "PATANJALI":"Patanjali Foods","RECLTD":"REC","SAIL":"Steel Authority of India (SAIL)",
    "SBICARD":"SBI Cards","SBILIFE":"SBI Life Insurance","SHREECEM":"Shree Cement",
    "SHRIRAMFIN":"Shriram Finance","SIEMENS":"Siemens India","SOLARINDS":"Solar Industries India",
    "SONACOMS":"Sona BLW Precision Forgings","SRF":"SRF","SBIN":"State Bank of India",
    "SUNPHARMA":"Sun Pharma","SUPREMEIND":"Supreme Industries","SUZLON":"Suzlon Energy",
    "SWIGGY":"Swiggy","TATAELXSI":"Tata Elxsi","TATACONSUM":"Tata Consumer Products",
    "TATAMOTORS":"Tata Motors","TATAPOWER":"Tata Power","TATASTEEL":"Tata Steel",
    "TCS":"Tata Consultancy Services","TECHM":"Tech Mahindra","TITAN":"Titan Company",
    "TORNTPHARM":"Torrent Pharmaceuticals","TRENT":"Trent","TIINDIA":"Tube Investments of India",
    "TVSMOTOR":"TVS Motor","ULTRACEMCO":"UltraTech Cement","UNIONBANK":"Union Bank of India",
    "UPL":"UPL","UNITDSPR":"United Spirits","VBL":"Varun Beverages","VEDL":"Vedanta",
    "VMM":"Vishal Mega Mart","VOLTAS":"Voltas","WAAREEENER":"Waaree Energies","WIPRO":"Wipro",
    "YESBANK":"Yes Bank","ETERNAL":"Eternal (Zomato)",
}

# NSE index symbols to exclude from F&O stock list
_FNO_EXCLUDE = {
    "NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","NIFTYNXT50",
    "NIFTYIT","UNDERLYING","SENSEX","BANKEX","NIFTY50","NIFTY100",
}

@st.cache_data(ttl=86400, show_spinner=False)
def _fetch_fno_symbols():
    """
    Fetch live NSE F&O equity list from NSE's fo_mktlots.csv.
    Returns a sorted list of NSE symbols, or None on failure.
    Cached for 24 hours so it's fetched once per day.
    """
    try:
        import requests, io, re
        sess = requests.Session()
        sess.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        })
        # Establish a session/cookie first
        sess.get("https://www.nseindia.com/", timeout=10)
        r = sess.get(
            "https://archives.nseindia.com/content/fo/fo_mktlots.csv",
            headers={"Referer": "https://www.nseindia.com/"},
            timeout=15,
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        col = df.iloc[:, 0].dropna().astype(str).str.strip()
        syms = [
            s for s in col
            if re.match(r'^[A-Z][A-Z0-9&\-]{1,19}$', s) and s not in _FNO_EXCLUDE
        ]
        if len(syms) >= 50:
            return sorted(set(syms))
    except Exception:
        pass
    return None

_fno_live   = _fetch_fno_symbols()
_fno_source = "NSE Live" if _fno_live else "Bundled"
_FNO = (
    [(s, s, _COMPANY_NAMES.get(s, s)) for s in _fno_live]
    if _fno_live
    else [(s, s, name) for s, name in sorted(_COMPANY_NAMES.items())]
)

_SECTOR = {
    # Financial Services
    "ABCAPITAL":"Financial Services","AXISBANK":"Financial Services",
    "BAJAJFINSV":"Financial Services","BAJFINANCE":"Financial Services",
    "BAJAJHLDNG":"Financial Services","BANDHANBNK":"Financial Services",
    "BANKBARODA":"Financial Services","BANKINDIA":"Financial Services",
    "BSE":"Financial Services","CAMS":"Financial Services",
    "CANBK":"Financial Services","CDSL":"Financial Services",
    "CHOLAFIN":"Financial Services","HDFCAMC":"Financial Services",
    "HDFCBANK":"Financial Services","HDFCLIFE":"Financial Services",
    "ICICIBANK":"Financial Services","ICICIGI":"Financial Services",
    "ICICIPRULI":"Financial Services","IDFCFIRSTB":"Financial Services",
    "IEX":"Financial Services","INDUSINDBK":"Financial Services",
    "INDIANB":"Financial Services","IRFC":"Financial Services",
    "JIOFIN":"Financial Services","KFINTECH":"Financial Services",
    "KOTAKBANK":"Financial Services","LICHSGFIN":"Financial Services",
    "LICI":"Financial Services","LTF":"Financial Services",
    "MANAPPURAM":"Financial Services","MFSL":"Financial Services",
    "MOTILALOFS":"Financial Services","MUTHOOTFIN":"Financial Services",
    "NAM-INDIA":"Financial Services","PFC":"Financial Services",
    "POLICYBZR":"Financial Services","PNB":"Financial Services",
    "PNBHOUSING":"Financial Services","RBLBANK":"Financial Services",
    "RECLTD":"Financial Services","SBICARD":"Financial Services",
    "SBILIFE":"Financial Services","SHRIRAMFIN":"Financial Services",
    "SBIN":"Financial Services","UNIONBANK":"Financial Services",
    "YESBANK":"Financial Services","360ONE":"Financial Services",
    # Information Technology
    "HCLTECH":"IT","INFY":"IT","KPITTECH":"IT","LTM":"IT",
    "MPHASIS":"IT","OFSS":"IT","PERSISTENT":"IT","TECHM":"IT",
    "TCS":"IT","WIPRO":"IT","COFORGE":"IT","TATAELXSI":"IT",
    # Pharma
    "ALKEM":"Pharma","AUROPHARMA":"Pharma","BIOCON":"Pharma",
    "CIPLA":"Pharma","DIVISLAB":"Pharma","DRREDDY":"Pharma",
    "GLENMARK":"Pharma","LAURUSLABS":"Pharma","LUPIN":"Pharma",
    "MANKIND":"Pharma","SUNPHARMA":"Pharma","TORNTPHARM":"Pharma",
    "ZYDUSLIFE":"Pharma",
    # Automobile
    "ASHOKLEY":"Automobile","BAJAJ-AUTO":"Automobile","EICHERMOT":"Automobile",
    "FORCEMOT":"Automobile","HEROMOTOCO":"Automobile","M&M":"Automobile",
    "MARUTI":"Automobile","TATAMOTORS":"Automobile","TVSMOTOR":"Automobile",
    "UNOMINDA":"Automobile","MOTHERSON":"Automobile",
    # Capital Goods
    "ABB":"Capital Goods","BDL":"Capital Goods","BEL":"Capital Goods",
    "BHARATFORG":"Capital Goods","BLUESTARCO":"Capital Goods",
    "BOSCHLTD":"Capital Goods","CGPOWER":"Capital Goods",
    "CUMMINSIND":"Capital Goods","DIXON":"Capital Goods","HAL":"Capital Goods",
    "HAVELLS":"Capital Goods","KEI":"Capital Goods","POLYCAB":"Capital Goods",
    "SIEMENS":"Capital Goods","TIINDIA":"Capital Goods","VOLTAS":"Capital Goods",
    "KAYNES":"Capital Goods","PGEL":"Capital Goods","SONACOMS":"Capital Goods",
    "GVT&D":"Capital Goods","POWERINDIA":"Capital Goods","AMBER":"Capital Goods",
    "APLAPOLLO":"Capital Goods","SOLARINDS":"Capital Goods",
    # Chemicals
    "PIDILITIND":"Chemicals","PIIND":"Chemicals","SRF":"Chemicals","UPL":"Chemicals",
    # Cement
    "AMBUJACEM":"Cement","DALBHARAT":"Cement","SHREECEM":"Cement",
    "ULTRACEMCO":"Cement","GRASIM":"Cement",
    # Consumer Goods
    "BRITANNIA":"Consumer Goods","COLPAL":"Consumer Goods","DABUR":"Consumer Goods",
    "DMART":"Consumer Goods","GODREJCP":"Consumer Goods","GODFRYPHLP":"Consumer Goods",
    "ITC":"Consumer Goods","JUBLFOOD":"Consumer Goods","MARICO":"Consumer Goods",
    "NESTLEIND":"Consumer Goods","PAGEIND":"Consumer Goods","PATANJALI":"Consumer Goods",
    "RADICO":"Consumer Goods","TITAN":"Consumer Goods","TATACONSUM":"Consumer Goods",
    "UNITDSPR":"Consumer Goods","VBL":"Consumer Goods","KALYANKJIL":"Consumer Goods",
    "HINDUNILVR":"Consumer Goods","CROMPTON":"Consumer Goods",
    # Metals & Mining
    "HINDALCO":"Metals & Mining","HINDZINC":"Metals & Mining","JSWSTEEL":"Metals & Mining",
    "JINDALSTEL":"Metals & Mining","NATIONALUM":"Metals & Mining","NMDC":"Metals & Mining",
    "SAIL":"Metals & Mining","TATASTEEL":"Metals & Mining","VEDL":"Metals & Mining",
    # Oil & Gas
    "BPCL":"Oil & Gas","GAIL":"Oil & Gas","HINDPETRO":"Oil & Gas",
    "IOC":"Oil & Gas","OIL":"Oil & Gas","ONGC":"Oil & Gas","PETRONET":"Oil & Gas",
    # Real Estate
    "DLF":"Real Estate","GODREJPROP":"Real Estate","LODHA":"Real Estate",
    "OBEROIRLTY":"Real Estate","PHOENIXLTD":"Real Estate","PRESTIGE":"Real Estate",
    # Power
    "ADANIGREEN":"Power","ADANIPOWER":"Power","ADANIENSOL":"Power",
    "JSWENERGY":"Power","NHPC":"Power","NTPC":"Power","POWERGRID":"Power",
    "SUZLON":"Power","TATAPOWER":"Power","WAAREEENER":"Power",
    "PREMIERENE":"Power","INOXWIND":"Power",
    # Healthcare
    "APOLLOHOSP":"Healthcare","FORTIS":"Healthcare","MAXHEALTH":"Healthcare",
    # Infrastructure
    "ADANIENT":"Infrastructure","ADANIPORTS":"Infrastructure",
    "GMRAIRPORT":"Infrastructure","RVNL":"Infrastructure",
    "NBCC":"Infrastructure","IREDA":"Infrastructure","MAZDOCK":"Infrastructure",
    "COCHINSHIP":"Infrastructure",
    # Telecom
    "BHARTIARTL":"Telecom","IDEA":"Telecom","INDUSTOWER":"Telecom",
    # Logistics / Aviation
    "INDIGO":"Aviation","DELHIVERY":"Logistics","CONCOR":"Logistics",
    # Others
    "ETERNAL":"E-Commerce","NYKAA":"E-Commerce","PAYTM":"Fintech","SWIGGY":"E-Commerce",
}

@st.cache_data(ttl=300)
def _fetch_fno_prices():
    import yfinance as yf
    nse_syms = [nse for _, nse, _ in _FNO]
    tickers  = [f"{s}.NS" for s in nse_syms]
    result = {}
    try:
        data = yf.download(tickers, period="2d", auto_adjust=True, progress=False)
        close_df = data["Close"]
        for nse, ticker in zip(nse_syms, tickers):
            try:
                series = close_df[ticker].dropna()
                if len(series) >= 2:
                    prev, cur = float(series.iloc[-2]), float(series.iloc[-1])
                    result[nse] = (round(cur, 2), round((cur - prev) / prev * 100, 2))
                elif len(series) == 1:
                    result[nse] = (round(float(series.iloc[-1]), 2), None)
            except Exception:
                pass
    except Exception:
        pass
    return result

# ── Stat bar ───────────────────────────────────────────────────────────────────
_s1, _s2, _s3 = st.columns(3)
_s1.metric("📋 F&O Stocks", len(_FNO))
_s2.markdown(f"""<div data-testid="metric-container" style="background:white;border-radius:10px;padding:1rem 1.2rem;box-shadow:0 1px 3px rgba(0,0,0,0.08);border-left:4px solid #3b82f6;">
<div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:500;">🏦 F&O List Source</div>
<div style="color:#0f172a;font-size:0.85rem;font-weight:600;margin-top:4px;">{_fno_source}</div>
</div>""", unsafe_allow_html=True)
_s3.markdown("""<div data-testid="metric-container" style="background:white;border-radius:10px;padding:1rem 1.2rem;box-shadow:0 1px 3px rgba(0,0,0,0.08);border-left:4px solid #3b82f6;">
<div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.05em;font-weight:500;">🔄 Prices</div>
<div style="color:#0f172a;font-size:0.85rem;font-weight:600;margin-top:4px;">On demand via yfinance</div>
</div>""", unsafe_allow_html=True)

# ── Section 1: Probable Upside — Next 1–2 Weeks ──────────────────────────────
st.markdown(f"""
<div class="section-header">
    <span class="section-header-title">🔮 Probable Upside — Next 1–2 Weeks</span>
    <span class="section-badge">11 signals</span>
</div>
<div class="section-body">
""", unsafe_allow_html=True)

st.caption("Screens all F&O stocks using 11 short-term technical signals — results cached for this session")

if st.button("🔮 Screen for Upside Candidates", key="load_swing"):
    st.session_state.pop("swing_data", None)
    st.session_state["swing_requested"] = True

if st.session_state.get("swing_requested"):
    if "swing_data" not in st.session_state:
        import yfinance as yf

        def _calc_ema(prices, n):
            k = 2 / (n + 1)
            e = prices[0]
            for p in prices[1:]:
                e = p * k + e * (1 - k)
            return e

        _nse_syms2 = [nse for _, nse, _ in _FNO]
        _tickers2  = [f"{s}.NS" for s in _nse_syms2]

        with st.spinner("Downloading price history for all F&O stocks…"):
            _hist2     = yf.download(_tickers2, period="1y", auto_adjust=True, progress=False)
            _close_df2 = _hist2["Close"]
            _vol_df2   = _hist2["Volume"]

        _swing_rows = []
        _prog2 = st.progress(0, text="Screening stocks…")

        for _i2, (_sym2, _nse2, _name2) in enumerate(_FNO):
            _prog2.progress((_i2 + 1) / len(_FNO), text=f"Analysing {_nse2}…")
            try:
                _ticker2 = f"{_nse2}.NS"
                _cls_s   = _close_df2[_ticker2].dropna()
                _vol_s   = _vol_df2[_ticker2].reindex(_cls_s.index).fillna(0)
                _cls     = list(_cls_s.astype(float))
                _vols    = list(_vol_s.astype(float))

                if len(_cls) < 20:
                    continue

                _cur          = _cls[-1]
                _sma20        = sum(_cls[-20:]) / 20
                _sma50        = sum(_cls[-min(50, len(_cls)):]) / min(50, len(_cls))
                _sma200       = sum(_cls[-200:]) / 200 if len(_cls) >= 200 else sum(_cls) / len(_cls)
                _sma20_rising = (sum(_cls[-5:]) / 5) > (sum(_cls[-10:-5]) / 5)

                _gains2  = [max(_cls[i] - _cls[i-1], 0) for i in range(1, len(_cls))]
                _losses2 = [max(_cls[i-1] - _cls[i], 0) for i in range(1, len(_cls))]
                _ag   = sum(_gains2[-14:])  / 14 if len(_gains2)  >= 14 else 0
                _al   = sum(_losses2[-14:]) / 14 if len(_losses2) >= 14 else 1
                _rsi2 = 100 - (100 / (1 + _ag / _al))

                _base5 = _cls[-6] if len(_cls) >= 6 else _cls[0]
                _ret5d = round((_cur - _base5) / _base5 * 100, 2) if _base5 else 0

                _avg20v    = sum(_vols[-20:]) / 20 if len(_vols) >= 20 else 0
                _avg5v     = sum(_vols[-5:])  / 5  if len(_vols) >= 5  else 0
                _vol_surge = bool(_avg20v and _avg5v > _avg20v * 1.1)

                _high20    = max(_cls[-20:])
                _near_high = _cur >= _high20 * 0.95

                _ema12     = _calc_ema(_cls[-30:], 12) if len(_cls) >= 30 else _cur
                _ema26     = _calc_ema(_cls[-50:], 26) if len(_cls) >= 50 else _cur
                _macd_bull = _ema12 > _ema26

                # 1. SMA20 > SMA50 (golden alignment)
                _golden_align = _sma20 > _sma50

                # 2. Price above SMA200 (long-term uptrend)
                _above_sma200 = _cur > _sma200

                # 3. MACD histogram positive (MACD line > 9-day signal line)
                _macd_series = []
                for _j in range(14, -1, -1):
                    _eidx = len(_cls) - _j
                    if _eidx >= 26:
                        _sl = _cls[max(0, _eidx - 60):_eidx]
                        _macd_series.append(_calc_ema(_sl, 12) - _calc_ema(_sl, 26))
                if len(_macd_series) >= 9:
                    _macd_sig_line  = _calc_ema(_macd_series, 9)
                    _macd_hist_bull = _macd_series[-1] > _macd_sig_line
                else:
                    _macd_hist_bull = _macd_bull

                # 4. 2+ consecutive up days (short-term momentum)
                _consec_up = (len(_cls) >= 3
                              and _cls[-1] > _cls[-2]
                              and _cls[-2] > _cls[-3])

                _st_score = sum([
                    _cur > _sma20,
                    _sma20_rising,
                    _cur > _sma50,
                    40 <= _rsi2 <= 65,
                    _ret5d > 0,
                    _vol_surge,
                    _near_high,
                    _golden_align,
                    _above_sma200,
                    _macd_hist_bull,
                    _consec_up,
                ])

                if _st_score >= 6:
                    _swing_rows.append({
                        "Stock":      _nse2,
                        "Sector":     _SECTOR.get(_nse2, "Other"),
                        "Price (₹)":  round(_cur, 2),
                        "5D Ret (%)": _ret5d,
                        "RSI":        round(_rsi2, 1),
                        "Vol Surge":  "✅" if _vol_surge      else "❌",
                        "Near High":  "✅" if _near_high      else "❌",
                        "MACD":       "✅" if _macd_bull      else "❌",
                        "SMA Align":  "✅" if _golden_align   else "❌",
                        "SMA200":     "✅" if _above_sma200   else "❌",
                        "MACD Hist":  "✅" if _macd_hist_bull else "❌",
                        "Consec Up":  "✅" if _consec_up      else "❌",
                        "Score /11":  _st_score,
                        "Chart":      f"https://www.tradingview.com/chart/?symbol=NSE:{_nse2}",
                    })
            except Exception:
                pass

        _prog2.empty()
        st.session_state["swing_data"] = _swing_rows

    _swing_data = st.session_state.get("swing_data", [])
    if _swing_data:
        _swing_df = (
            pd.DataFrame(_swing_data)
            .sort_values(["Score /11", "5D Ret (%)"], ascending=[False, False])
            .head(25)
            .reset_index(drop=True)
        )
        _swing_df.index += 1

        _strong = (_swing_df["Score /11"] >= 9).sum()
        st.markdown(
            f"**{len(_swing_df)} candidates** found (Score ≥ 6/11)  •  "
            f"**{_strong} strong setups** (Score ≥ 9/11)"
        )

        st.dataframe(
            _swing_df,
            use_container_width=True,
            height=min(600, 56 + len(_swing_df) * 35),
            column_config={
                "Stock":      st.column_config.TextColumn("Stock"),
                "Sector":     st.column_config.TextColumn("Sector"),
                "Price (₹)":  st.column_config.NumberColumn("Price (₹)",  format="₹%.2f"),
                "5D Ret (%)": st.column_config.NumberColumn("5D Ret (%)", format="%.2f%%"),
                "RSI":        st.column_config.NumberColumn("RSI",        format="%.1f"),
                "Vol Surge":  st.column_config.TextColumn("Vol Surge"),
                "Near High":  st.column_config.TextColumn("Near High"),
                "MACD":       st.column_config.TextColumn("MACD"),
                "SMA Align":  st.column_config.TextColumn("SMA Align"),
                "SMA200":     st.column_config.TextColumn("SMA200"),
                "MACD Hist":  st.column_config.TextColumn("MACD Hist"),
                "Consec Up":  st.column_config.TextColumn("Consec Up"),
                "Score /11":  st.column_config.NumberColumn("Score /11",  format="%d"),
                "Chart":      st.column_config.LinkColumn("TradingView",  display_text="📈 Open Chart"),
            },
        )
        st.caption(
            "Score /11 — above SMA20 · SMA20 rising · above SMA50 · RSI 40–65 · 5D return > 0 · "
            "vol surge · near 20D high · SMA20>SMA50 · above SMA200 · MACD histogram > 0 · 2+ consec up days  "
            "•  ⚠️ For informational purposes only — not financial advice"
        )
    else:
        st.info("No stocks met the screening criteria. Try again during market hours.")

st.markdown("</div>", unsafe_allow_html=True)  # close section-body

# ── Section 2: NSE F&O Stocks Table ──────────────────────────────────────────
st.markdown(f"""
<div class="section-header">
    <span class="section-header-title">📋 NSE F&amp;O Stocks</span>
    <span class="section-badge">{len(_FNO)} stocks</span>
</div>
<div class="section-body">
""", unsafe_allow_html=True)

if st.button("📥 Load Today's Prices", key="load_fno_prices"):
    with st.spinner("Fetching today's prices…"):
        st.session_state["fno_prices"] = _fetch_fno_prices()

fno_df = pd.DataFrame([{
    "Stock":   nse_sym,
    "Company": name,
    "Chart":   f"https://www.tradingview.com/chart/?symbol=NSE:{nse_sym}",
} for _, nse_sym, name in _FNO])

_prices = st.session_state.get("fno_prices", {})
if _prices:
    fno_df["Price (₹)"] = fno_df["Stock"].map(lambda s: _prices.get(s, (None, None))[0])
    fno_df["Day (%)"]   = fno_df["Stock"].map(lambda s: _prices.get(s, (None, None))[1])

_fno_search = st.text_input(
    "🔍 Search by symbol or company",
    key="fno_search",
    placeholder="e.g. RELIANCE, Infosys, HDFC…",
)
if _fno_search.strip():
    _q = _fno_search.strip()
    _mask = (
        fno_df["Stock"].str.contains(_q, case=False, na=False)
        | fno_df["Company"].str.contains(_q, case=False, na=False)
    )
    fno_df = fno_df[_mask].reset_index(drop=True)

_col_cfg = {
    "Stock":   st.column_config.TextColumn("Stock"),
    "Company": st.column_config.TextColumn("Company"),
    "Chart":   st.column_config.LinkColumn("TradingView", display_text="📈 Open Chart"),
}
if _prices:
    _col_cfg["Price (₹)"] = st.column_config.NumberColumn("Price (₹)", format="₹%.2f")
    _col_cfg["Day (%)"]   = st.column_config.NumberColumn("Day (%)",   format="%.2f%%")

st.dataframe(
    fno_df,
    use_container_width=True,
    height=min(600, 56 + len(fno_df) * 35),
    column_config=_col_cfg,
    hide_index=True,
)
st.caption(f"Showing {len(fno_df)} of {len(_FNO)} NSE F&O stocks")
st.markdown("</div>", unsafe_allow_html=True)  # close section-body
st.markdown("</div>", unsafe_allow_html=True)  # close content-wrap
