import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta

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
    max-width: 100% !important;
}

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
.content-wrap { padding: 1.4rem 2rem; }

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
    margin-top: 1.4rem;
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

# ── Sidebar — optional credentials for live-data sections ─────────────────────
if "api_key" not in st.session_state:
    saved = _load_creds()
    st.session_state["api_key"]       = saved.get("api_key", "")
    st.session_state["api_secret"]    = saved.get("api_secret", "")
    st.session_state["session_token"] = saved.get("session_token", "")

with st.sidebar:
    st.markdown("""
    <div style="padding:1.2rem 0.5rem 1rem; border-bottom:1px solid #1e293b; margin-bottom:1rem;">
        <div style="font-size:1.1rem;font-weight:700;color:#f8fafc;letter-spacing:-0.02em;">📊 F&amp;O Analysis</div>
        <div style="font-size:0.72rem;color:#64748b;margin-top:3px;">NSE Derivatives Screener</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("**🔑 ICICIdirect Credentials**")
    st.caption("Required only for the Upside Screener section.")
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

    connect = st.button("🔌 Connect", type="primary", use_container_width=True)

    if os.path.exists(CREDS_FILE):
        if st.button("🗑 Clear saved credentials", use_container_width=True):
            _clear_creds()
            st.rerun()
        st.caption("✅ Credentials loaded from last session.")
    else:
        st.caption("Credentials will be saved locally after you connect.")

# ── Top Navbar ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="top-navbar">
    <div>
        <div class="nav-title">📊 NSE F&amp;O Analysis</div>
        <div class="nav-subtitle">Futures &amp; Options Screener — Powered by ICICIdirect Breeze Connect</div>
    </div>
    <span class="nav-badge">NSE Live</span>
</div>
<div class="content-wrap" style="padding-bottom:0">
""", unsafe_allow_html=True)

# ── NSE F&O Stock List — sourced from ICICIdirect SecurityMaster ───────────────
# Tuple: (breeze_code, nse_symbol, company_name)
_FNO = [
    ("ABB",      "ABB",         "ABB India"),
    ("ABBPOW",   "POWERINDIA",  "Hitachi Energy India"),
    ("ADAENT",   "ADANIENT",    "Adani Enterprises"),
    ("ADAGRE",   "ADANIGREEN",  "Adani Green Energy"),
    ("ADAPOR",   "ADANIPORTS",  "Adani Ports & SEZ"),
    ("ADAPOW",   "ADANIPOWER",  "Adani Power"),
    ("ADATRA",   "ADANIENSOL",  "Adani Energy Solutions"),
    ("ADICAP",   "ABCAPITAL",   "Aditya Birla Capital"),
    ("ALKLAB",   "ALKEM",       "Alkem Laboratories"),
    ("ALSTD",    "GVT&D",       "GE Vernova T&D India"),
    ("AMBCE",    "AMBUJACEM",   "Ambuja Cements"),
    ("AMBEN",    "AMBER",       "Amber Enterprises India"),
    ("ANGBRO",   "ANGELONE",    "Angel One"),
    ("APLAPO",   "APLAPOLLO",   "APL Apollo Tubes"),
    ("APOHOS",   "APOLLOHOSP",  "Apollo Hospitals"),
    ("ASHLEY",   "ASHOKLEY",    "Ashok Leyland"),
    ("ASIPAI",   "ASIANPAINT",  "Asian Paints"),
    ("ASTPOL",   "ASTRAL",      "Astral"),
    ("AURPHA",   "AUROPHARMA",  "Aurobindo Pharma"),
    ("AUSMA",    "AUBANK",      "AU Small Finance Bank"),
    ("AVESUP",   "DMART",       "Avenue Supermarts (D-Mart)"),
    ("AXIBAN",   "AXISBANK",    "Axis Bank"),
    ("BAAUTO",   "BAJAJ-AUTO",  "Bajaj Auto"),
    ("BAFINS",   "BAJAJFINSV",  "Bajaj Finserv"),
    ("BAJFI",    "BAJFINANCE",  "Bajaj Finance"),
    ("BAJHOL",   "BAJAJHLDNG",  "Bajaj Holdings"),
    ("BANBAN",   "BANDHANBNK",  "Bandhan Bank"),
    ("BANBAR",   "BANKBARODA",  "Bank of Baroda"),
    ("BANIND",   "BANKINDIA",   "Bank of India"),
    ("BHAAIR",   "BHARTIARTL",  "Bharti Airtel"),
    ("BHADYN",   "BDL",         "Bharat Dynamics"),
    ("BHAELE",   "BEL",         "Bharat Electronics"),
    ("BHAFOR",   "BHARATFORG",  "Bharat Forge"),
    ("BHAINF",   "INDUSTOWER",  "Indus Towers"),
    ("BHAPET",   "BPCL",        "BPCL"),
    ("BHEL",     "BHEL",        "BHEL"),
    ("BIOCON",   "BIOCON",      "Biocon"),
    ("BLUSTA",   "BLUESTARCO",  "Blue Star"),
    ("BOSLIM",   "BOSCHLTD",    "Bosch India"),
    ("BRIIND",   "BRITANNIA",   "Britannia Industries"),
    ("BSE",      "BSE",         "BSE"),
    ("CADHEA",   "ZYDUSLIFE",   "Zydus Lifesciences"),
    ("CANBAN",   "CANBK",       "Canara Bank"),
    ("CDSL",     "CDSL",        "CDSL"),
    ("CHOINV",   "CHOLAFIN",    "Cholamandalam Investment & Finance"),
    ("CIPLA",    "CIPLA",       "Cipla"),
    ("COALIN",   "COALINDIA",   "Coal India"),
    ("COCSHI",   "COCHINSHIP",  "Cochin Shipyard"),
    ("COLPAL",   "COLPAL",      "Colgate-Palmolive India"),
    ("COMAGE",   "CAMS",        "CAMS"),
    ("CONCOR",   "CONCOR",      "Container Corp of India"),
    ("CROGR",    "CROMPTON",    "Crompton Greaves Consumer"),
    ("CROGRE",   "CGPOWER",     "CG Power"),
    ("CUMIND",   "CUMMINSIND",  "Cummins India"),
    ("DABIND",   "DABUR",       "Dabur India"),
    ("DELLIM",   "DELHIVERY",   "Delhivery"),
    ("DIVLAB",   "DIVISLAB",    "Divi's Laboratories"),
    ("DIXTEC",   "DIXON",       "Dixon Technologies"),
    ("DLFLIM",   "DLF",         "DLF"),
    ("DRREDD",   "DRREDDY",     "Dr. Reddy's Laboratories"),
    ("EICMOT",   "EICHERMOT",   "Eicher Motors"),
    ("FEDBAN",   "FEDERALBNK",  "Federal Bank"),
    ("FORHEA",   "FORTIS",      "Fortis Healthcare"),
    ("FORMOT",   "FORCEMOT",    "Force Motors"),
    ("FSNECO",   "NYKAA",       "Nykaa (FSN E-Commerce)"),
    ("GAIL",     "GAIL",        "GAIL India"),
    ("GLEPHA",   "GLENMARK",    "Glenmark Pharmaceuticals"),
    ("GMRINF",   "GMRAIRPORT",  "GMR Airports"),
    ("GODCON",   "GODREJCP",    "Godrej Consumer Products"),
    ("GODPHI",   "GODFRYPHLP",  "Godfrey Phillips India"),
    ("GODPRO",   "GODREJPROP",  "Godrej Properties"),
    ("GRASIM",   "GRASIM",      "Grasim Industries"),
    ("HAVIND",   "HAVELLS",     "Havells India"),
    ("HCLTEC",   "HCLTECH",     "HCL Technologies"),
    ("HDFAMC",   "HDFCAMC",     "HDFC AMC"),
    ("HDFBAN",   "HDFCBANK",    "HDFC Bank"),
    ("HDFSTA",   "HDFCLIFE",    "HDFC Life Insurance"),
    ("HERHON",   "HEROMOTOCO",  "Hero MotoCorp"),
    ("HINAER",   "HAL",         "Hindustan Aeronautics (HAL)"),
    ("HINDAL",   "HINDALCO",    "Hindalco Industries"),
    ("HINLEV",   "HINDUNILVR",  "Hindustan Unilever"),
    ("HINPET",   "HINDPETRO",   "HPCL"),
    ("HINZIN",   "HINDZINC",    "Hindustan Zinc"),
    ("HYUMOT",   "HYUNDAI",     "Hyundai Motor India"),
    ("ICIBAN",   "ICICIBANK",   "ICICI Bank"),
    ("ICILOM",   "ICICIGI",     "ICICI Lombard General Insurance"),
    ("ICIPRU",   "ICICIPRULI",  "ICICI Prudential Life Insurance"),
    ("IDECEL",   "IDEA",        "Vodafone Idea"),
    ("IDFBAN",   "IDFCFIRSTB",  "IDFC First Bank"),
    ("IIFWEA",   "360ONE",      "360 ONE WAM"),
    ("INDBA",    "INDUSINDBK",  "IndusInd Bank"),
    ("INDEN",    "IEX",         "Indian Energy Exchange"),
    ("INDHOT",   "INDHOTEL",    "Indian Hotels (Taj)"),
    ("INDIBA",   "INDIANB",     "Indian Bank"),
    ("INDOIL",   "IOC",         "Indian Oil Corp"),
    ("INDR",     "IRFC",        "IRFC"),
    ("INDREN",   "IREDA",       "IREDA"),
    ("INFEDG",   "NAUKRI",      "Info Edge (Naukri)"),
    ("INFTEC",   "INFY",        "Infosys"),
    ("INOWIN",   "INOXWIND",    "INOX Wind"),
    ("INTAVI",   "INDIGO",      "IndiGo (InterGlobe Aviation)"),
    ("ITC",      "ITC",         "ITC"),
    ("JINSP",    "JINDALSTEL",  "Jindal Steel & Power"),
    ("JIOFIN",   "JIOFIN",      "Jio Financial Services"),
    ("JSWENE",   "JSWENERGY",   "JSW Energy"),
    ("JSWSTE",   "JSWSTEEL",    "JSW Steel"),
    ("JUBFOO",   "JUBLFOOD",    "Jubilant FoodWorks"),
    ("KALJEW",   "KALYANKJIL",  "Kalyan Jewellers"),
    ("KAYTEC",   "KAYNES",      "Kaynes Technology"),
    ("KEIIND",   "KEI",         "KEI Industries"),
    ("KFITEC",   "KFINTECH",    "KFin Technologies"),
    ("KOTMAH",   "KOTAKBANK",   "Kotak Mahindra Bank"),
    ("KPITE",    "KPITTECH",    "KPIT Technologies"),
    ("LARTOU",   "LT",          "Larsen & Toubro"),
    ("LAULAB",   "LAURUSLABS",  "Laurus Labs"),
    ("LIC",      "LICI",        "LIC India"),
    ("LICHF",    "LICHSGFIN",   "LIC Housing Finance"),
    ("LTFINA",   "LTF",         "L&T Finance"),
    ("LTINFO",   "LTM",         "LTIMindtree"),
    ("LUPIN",    "LUPIN",       "Lupin"),
    ("MACDEV",   "LODHA",       "Lodha Developers"),
    ("MAHMAH",   "M&M",         "Mahindra & Mahindra"),
    ("MANAFI",   "MANAPPURAM",  "Manappuram Finance"),
    ("MAPHA",    "MANKIND",     "Mankind Pharma"),
    ("MARLIM",   "MARICO",      "Marico"),
    ("MARUTI",   "MARUTI",      "Maruti Suzuki"),
    ("MAXFIN",   "MFSL",        "Max Financial Services"),
    ("MAXHEA",   "MAXHEALTH",   "Max Healthcare"),
    ("MAZDOC",   "MAZDOCK",     "Mazagon Dock Shipbuilders"),
    ("MCX",      "MCX",         "MCX"),
    ("MININD",   "UNOMINDA",    "UNO Minda"),
    ("MOTOSW",   "MOTILALOFS",  "Motilal Oswal Financial Services"),
    ("MOTSUM",   "MOTHERSON",   "Motherson Sumi Systems"),
    ("MPHLIM",   "MPHASIS",     "Mphasis"),
    ("MUTFIN",   "MUTHOOTFIN",  "Muthoot Finance"),
    ("NATALU",   "NATIONALUM",  "National Aluminium"),
    ("NATMIN",   "NMDC",        "NMDC"),
    ("NBCC",     "NBCC",        "NBCC India"),
    ("NESIND",   "NESTLEIND",   "Nestlé India"),
    ("NHPC",     "NHPC",        "NHPC"),
    ("NIITEC",   "COFORGE",     "Coforge"),
    ("NTPC",     "NTPC",        "NTPC"),
    ("OBEREA",   "OBEROIRLTY",  "Oberoi Realty"),
    ("ODICEM",   "DALBHARAT",   "Dalmia Bharat"),
    ("OILIND",   "OIL",         "Oil India"),
    ("ONE97",    "PAYTM",       "Paytm (One 97 Communications)"),
    ("ONGC",     "ONGC",        "ONGC"),
    ("ORAFIN",   "OFSS",        "Oracle Financial Services"),
    ("PAGIND",   "PAGEIND",     "Page Industries"),
    ("PBFINT",   "POLICYBZR",   "PB Fintech (Policybazaar)"),
    ("PERSYS",   "PERSISTENT",  "Persistent Systems"),
    ("PETLNG",   "PETRONET",    "Petronet LNG"),
    ("PGELEC",   "PGEL",        "PG Electroplast"),
    ("PHOMIL",   "PHOENIXLTD",  "Phoenix Mills"),
    ("PIDIND",   "PIDILITIND",  "Pidilite Industries"),
    ("PIIND",    "PIIND",       "PI Industries"),
    ("PNBHOU",   "PNBHOUSING",  "PNB Housing Finance"),
    ("POLI",     "POLYCAB",     "Polycab India"),
    ("POWFIN",   "PFC",         "Power Finance Corp (PFC)"),
    ("POWGRI",   "POWERGRID",   "Power Grid Corp"),
    ("PREENR",   "PREMIERENE",  "Premier Energies"),
    ("PREEST",   "PRESTIGE",    "Prestige Estates Projects"),
    ("PUNBAN",   "PNB",         "Punjab National Bank"),
    ("RADKHA",   "RADICO",      "Radico Khaitan"),
    ("RAIVIK",   "RVNL",        "Rail Vikas Nigam (RVNL)"),
    ("RBLBAN",   "RBLBANK",     "RBL Bank"),
    ("RELIND",   "RELIANCE",    "Reliance Industries"),
    ("RELNIP",   "NAM-INDIA",   "Nippon India AMC"),
    ("RUCSOY",   "PATANJALI",   "Patanjali Foods"),
    ("RURELE",   "RECLTD",      "REC"),
    ("SAIL",     "SAIL",        "Steel Authority of India (SAIL)"),
    ("SBICAR",   "SBICARD",     "SBI Cards"),
    ("SBILIF",   "SBILIFE",     "SBI Life Insurance"),
    ("SHRCEM",   "SHREECEM",    "Shree Cement"),
    ("SHRTRA",   "SHRIRAMFIN",  "Shriram Finance"),
    ("SIEMEN",   "SIEMENS",     "Siemens India"),
    ("SOLIN",    "SOLARINDS",   "Solar Industries India"),
    ("SONBLW",   "SONACOMS",    "Sona BLW Precision Forgings"),
    ("SRF",      "SRF",         "SRF"),
    ("STABAN",   "SBIN",        "State Bank of India"),
    ("SUNPHA",   "SUNPHARMA",   "Sun Pharma"),
    ("SUPIND",   "SUPREMEIND",  "Supreme Industries"),
    ("SUZENE",   "SUZLON",      "Suzlon Energy"),
    ("SWILIM",   "SWIGGY",      "Swiggy"),
    ("TATELX",   "TATAELXSI",   "Tata Elxsi"),
    ("TATGLO",   "TATACONSUM",  "Tata Consumer Products"),
    ("TATMOT",   "TATAMOTORS",  "Tata Motors"),
    ("TATPOW",   "TATAPOWER",   "Tata Power"),
    ("TATSTE",   "TATASTEEL",   "Tata Steel"),
    ("TCS",      "TCS",         "Tata Consultancy Services"),
    ("TECMAH",   "TECHM",       "Tech Mahindra"),
    ("TITIND",   "TITAN",       "Titan Company"),
    ("TORPHA",   "TORNTPHARM",  "Torrent Pharmaceuticals"),
    ("TRENT",    "TRENT",       "Trent"),
    ("TUBIN",    "TIINDIA",     "Tube Investments of India"),
    ("TVSMOT",   "TVSMOTOR",    "TVS Motor"),
    ("ULTCEM",   "ULTRACEMCO",  "UltraTech Cement"),
    ("UNIBAN",   "UNIONBANK",   "Union Bank of India"),
    ("UNIP",     "UPL",         "UPL"),
    ("UNISPI",   "UNITDSPR",    "United Spirits"),
    ("VARBEV",   "VBL",         "Varun Beverages"),
    ("VEDLIM",   "VEDL",        "Vedanta"),
    ("VISMEG",   "VMM",         "Vishal Mega Mart"),
    ("VOLTAS",   "VOLTAS",      "Voltas"),
    ("WAAENE",   "WAAREEENER",  "Waaree Energies"),
    ("WIPRO",    "WIPRO",       "Wipro"),
    ("YESBAN",   "YESBANK",     "Yes Bank"),
    ("ZOMLIM",   "ETERNAL",     "Eternal (Zomato)"),
]

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
_s2.metric("🏦 Data Source", "ICICIdirect")
_s3.metric("🔄 Prices", "On demand via yfinance")

# ── Section 1: NSE F&O Stocks Table ───────────────────────────────────────────
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
st.markdown("</div>", unsafe_allow_html=True)

# ── Live-data sections — require Breeze connection ─────────────────────────────
_already_connected = st.session_state.get("breeze_connected", False)
_has_creds = bool(api_key and api_secret and session_token)

breeze = None

if connect or _already_connected:
    if not _has_creds:
        st.warning("Please fill in all three credential fields in the sidebar to load live data.")
    else:
        with st.spinner("Connecting to ICICIdirect…"):
            try:
                from breeze_connect import BreezeConnect
                breeze = BreezeConnect(api_key=api_key)
                breeze.generate_session(api_secret=api_secret, session_token=session_token)
                _save_creds(api_key, api_secret, session_token)
                st.session_state["api_key"]          = api_key
                st.session_state["api_secret"]       = api_secret
                st.session_state["session_token"]    = session_token
                st.session_state["breeze_connected"] = True
            except Exception as e:
                st.error(f"Connection failed: {e}")
                _clear_creds()
                st.session_state["breeze_connected"] = False
                breeze = None
else:
    st.info(
        "📡 Enter your ICICIdirect credentials in the sidebar and click **Connect** "
        "to unlock the **Upside Screener** section below."
    )

# ── Section 2: Probable Upside — Next 1–2 Weeks ───────────────────────────────
st.markdown(f"""
<div class="section-header">
    <span class="section-header-title">🔮 Probable Upside — Next 1–2 Weeks</span>
    <span class="section-badge">11 signals</span>
</div>
<div class="section-body">
""", unsafe_allow_html=True)

if breeze is None:
    st.caption("Connect via the sidebar to run the upside screener.")
else:
    st.caption("Screens all F&O stocks using 11 short-term technical signals — results cached for this session")

    if st.button("🔮 Screen for Upside Candidates", key="load_swing"):
        st.session_state.pop("swing_data", None)
        st.session_state["swing_requested"] = True

    if st.session_state.get("swing_requested"):
        if "swing_data" not in st.session_state:
            _today2 = datetime.now()
            _from2  = _today2 - timedelta(days=280)

            def _calc_ema(prices, n):
                k = 2 / (n + 1)
                e = prices[0]
                for p in prices[1:]:
                    e = p * k + e * (1 - k)
                return e

            _swing_rows = []
            _prog2 = st.progress(0, text="Screening stocks…")

            for _i2, (_sym2, _nse2, _name2) in enumerate(_FNO):
                _prog2.progress((_i2 + 1) / len(_FNO), text=f"Analysing {_sym2}…")
                try:
                    _raw2 = []
                    for _pt2 in ["cash", ""]:
                        _r2 = breeze.get_historical_data_v2(
                            interval="1day",
                            from_date=_from2.strftime("%Y-%m-%dT07:00:00.000Z"),
                            to_date=_today2.strftime("%Y-%m-%dT15:30:00.000Z"),
                            stock_code=_sym2,
                            exchange_code="NSE",
                            product_type=_pt2,
                        )
                        if _r2.get("Status") == 200 and _r2.get("Success"):
                            _raw2 = _r2["Success"]
                            if len(_raw2) >= 20:
                                break

                    if len(_raw2) < 20:
                        continue

                    _cls  = [float(d.get("close",  0) or 0) for d in _raw2 if d.get("close")]
                    _vols = [float(d.get("volume", 0) or 0) for d in _raw2]

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

                    # ── 4 new signals ───────────────────────────────────────
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
                        _macd_sig_line = _calc_ema(_macd_series, 9)
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
                            "Stock":         _nse2,
                            "Sector":        _SECTOR.get(_nse2, "Other"),
                            "Price (₹)":     round(_cur, 2),
                            "5D Ret (%)":    _ret5d,
                            "RSI":           round(_rsi2, 1),
                            "Vol Surge":     "✅" if _vol_surge     else "❌",
                            "Near High":     "✅" if _near_high     else "❌",
                            "MACD":          "✅" if _macd_bull     else "❌",
                            "SMA Align":     "✅" if _golden_align  else "❌",
                            "SMA200":        "✅" if _above_sma200  else "❌",
                            "MACD Hist":     "✅" if _macd_hist_bull else "❌",
                            "Consec Up":     "✅" if _consec_up     else "❌",
                            "Score /11":     _st_score,
                            "Chart":         f"https://www.tradingview.com/chart/?symbol=NSE:{_nse2}",
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
st.markdown("</div>", unsafe_allow_html=True)  # close content-wrap
