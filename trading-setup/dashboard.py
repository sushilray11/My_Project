import warnings
warnings.filterwarnings("ignore")

import time
import threading
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Trading Setup",
    page_icon="📈",
    layout="wide",
)

st.markdown("""
<style>
  /* Reduce Streamlit's default top padding */
  .block-container { padding-top: 2rem !important; padding-bottom: 0.5rem !important; }
  /* Shrink the title */
  h1 { font-size: 1.5rem !important; margin-bottom: 0 !important; padding-bottom: 0 !important; }
  /* Tighten caption under title */
  .stCaptionContainer { margin-top: 0 !important; margin-bottom: 0.25rem !important; }
  /* Remove extra gap above radio */
  div[data-testid="stRadio"] { margin-top: 0.25rem !important; margin-bottom: 0 !important; }
  /* Smaller metric numbers */
  div[data-testid="stMetricValue"] { font-size: 1.4rem !important; }
  div[data-testid="stMetricLabel"] { font-size: 0.8rem !important; }
</style>
""", unsafe_allow_html=True)

st.title("📈 Short-Term Trading Setup — NSE / BSE")
st.caption("Strategy: EMA 9/21 Crossover + RSI Confirmation + Volume Filter")

# ── NSE stock master list (name → ticker) ─────────────────────────────────────
NSE_STOCKS = {
    # Indices
    "Nifty 50 (Index)"                     : "^NSEI",
    "Bank Nifty (Index)"                   : "^NSEBANK",
    "Nifty IT (Index)"                     : "^CNXIT",
    # Large cap / Nifty 50
    "Reliance Industries"                  : "RELIANCE.NS",
    "Tata Consultancy Services (TCS)"      : "TCS.NS",
    "Infosys"                              : "INFY.NS",
    "HDFC Bank"                            : "HDFCBANK.NS",
    "ICICI Bank"                           : "ICICIBANK.NS",
    "Wipro"                                : "WIPRO.NS",
    "HCL Technologies"                     : "HCLTECH.NS",
    "Axis Bank"                            : "AXISBANK.NS",
    "State Bank of India (SBI)"            : "SBIN.NS",
    "Kotak Mahindra Bank"                  : "KOTAKBANK.NS",
    "Bajaj Finance"                        : "BAJFINANCE.NS",
    "Bajaj Finserv"                        : "BAJAJFINSV.NS",
    "Maruti Suzuki"                        : "MARUTI.NS",
    "Asian Paints"                         : "ASIANPAINT.NS",
    "Hindustan Unilever (HUL)"             : "HINDUNILVR.NS",
    "Larsen & Toubro (L&T)"                : "LT.NS",
    "Sun Pharmaceutical"                   : "SUNPHARMA.NS",
    "Tata Motors"                          : "TATAMOTORS.NS",
    "Tata Steel"                           : "TATASTEEL.NS",
    "Power Grid Corporation"               : "POWERGRID.NS",
    "NTPC"                                 : "NTPC.NS",
    "Oil & Natural Gas (ONGC)"             : "ONGC.NS",
    "Bharti Airtel"                        : "BHARTIARTL.NS",
    "ITC"                                  : "ITC.NS",
    "Nestle India"                         : "NESTLEIND.NS",
    "Dr Reddy's Laboratories"              : "DRREDDY.NS",
    "Cipla"                                : "CIPLA.NS",
    "Divis Laboratories"                   : "DIVISLAB.NS",
    "Eicher Motors"                        : "EICHERMOT.NS",
    "Hero MotoCorp"                        : "HEROMOTOCO.NS",
    "JSW Steel"                            : "JSWSTEEL.NS",
    "Hindalco Industries"                  : "HINDALCO.NS",
    "Adani Ports"                          : "ADANIPORTS.NS",
    "Adani Enterprises"                    : "ADANIENT.NS",
    "Adani Green Energy"                   : "ADANIGREEN.NS",
    "UltraTech Cement"                     : "ULTRACEMCO.NS",
    "Grasim Industries"                    : "GRASIM.NS",
    "Britannia Industries"                 : "BRITANNIA.NS",
    "IndusInd Bank"                        : "INDUSINDBK.NS",
    "Titan Company"                        : "TITAN.NS",
    "Tech Mahindra"                        : "TECHM.NS",
    "Mahindra & Mahindra (M&M)"            : "M&M.NS",
    "Bajaj Auto"                           : "BAJAJ-AUTO.NS",
    "Coal India"                           : "COALINDIA.NS",
    "SBI Life Insurance"                   : "SBILIFE.NS",
    "HDFC Life Insurance"                  : "HDFCLIFE.NS",
    "Divi's Laboratories"                  : "DIVISLAB.NS",
    # Mid cap
    "Zomato"                               : "ZOMATO.NS",
    "Paytm (One97 Communications)"         : "PAYTM.NS",
    "Nykaa (FSN E-Commerce)"               : "NYKAA.NS",
    "Delhivery"                            : "DELHIVERY.NS",
    "PB Fintech (Policybazaar)"            : "POLICYBZR.NS",
    "Persistent Systems"                   : "PERSISTENT.NS",
    "Mphasis"                              : "MPHASIS.NS",
    "Coforge"                              : "COFORGE.NS",
    "L&T Infotech (LTIMindtree)"           : "LTIM.NS",
    "Tata Elxsi"                           : "TATAELXSI.NS",
    "Kpit Technologies"                    : "KPITTECH.NS",
    "Zensar Technologies"                  : "ZENSARTECH.NS",
    "Birlasoft"                            : "BSOFT.NS",
    "Intellect Design Arena"               : "INTELLECTDS.NS",
    "Mastek"                               : "MASTEK.NS",
    "Happiest Minds Technologies"          : "HAPPSTMNDS.NS",
    "Tata Communication"                   : "TATACOMM.NS",
    "Indraprastha Gas (IGL)"               : "IGL.NS",
    "Mahanagar Gas (MGL)"                  : "MGL.NS",
    "Gujarat Gas"                          : "GUJGASLTD.NS",
    "Petronet LNG"                         : "PETRONET.NS",
    "GAIL India"                           : "GAIL.NS",
    "Havells India"                        : "HAVELLS.NS",
    "Crompton Greaves Consumer"            : "CROMPTON.NS",
    "Voltas"                               : "VOLTAS.NS",
    "Whirlpool of India"                   : "WHIRLPOOL.NS",
    "Dixon Technologies"                   : "DIXON.NS",
    "Amber Enterprises"                    : "AMBER.NS",
    "Godrej Consumer Products"             : "GODREJCP.NS",
    "Pidilite Industries"                  : "PIDILITIND.NS",
    "Berger Paints"                        : "BERGEPAINT.NS",
    "Kansai Nerolac Paints"                : "KANSAINER.NS",
    "Astral"                               : "ASTRAL.NS",
    "Supreme Industries"                   : "SUPREMEIND.NS",
    "PI Industries"                        : "PIIND.NS",
    "UPL"                                  : "UPL.NS",
    "Bayer CropScience"                    : "BAYERCROP.NS",
    "Shree Cement"                         : "SHREECEM.NS",
    "ACC"                                  : "ACC.NS",
    "Ambuja Cements"                       : "AMBUJACEM.NS",
    "JK Cement"                            : "JKCEMENT.NS",
    "Dalmia Bharat"                        : "DALBHARAT.NS",
    "Torrent Pharmaceuticals"              : "TORNTPHARM.NS",
    "Lupin"                                : "LUPIN.NS",
    "Alkem Laboratories"                   : "ALKEM.NS",
    "Abbott India"                         : "ABBOTINDIA.NS",
    "Pfizer India"                         : "PFIZER.NS",
    "Max Healthcare"                       : "MAXHEALTH.NS",
    "Apollo Hospitals"                     : "APOLLOHOSP.NS",
    "Fortis Healthcare"                    : "FORTIS.NS",
    "Metropolis Healthcare"                : "METROPOLIS.NS",
    "Thyrocare Technologies"               : "THYROCARE.NS",
    "IRCTC"                                : "IRCTC.NS",
    "Indian Railways Finance (IRFC)"       : "IRFC.NS",
    "Rail Vikas Nigam (RVNL)"              : "RVNL.NS",
    "Container Corporation (CONCOR)"       : "CONCOR.NS",
    "Interglobe Aviation (IndiGo)"         : "INDIGO.NS",
    "SpiceJet"                             : "SPICEJET.NS",
    # Small cap / others
    "Syrma SGS Technology"                 : "SYRMA.NS",
    "Kaynes Technology"                    : "KAYNES.NS",
    "Avalon Technologies"                  : "AVALON.NS",
    "Elin Electronics"                     : "ELIN.NS",
    "Vedant Fashions (Manyavar)"           : "MANYAVAR.NS",
    "Campus Activewear"                    : "CAMPUS.NS",
    "Metro Brands"                         : "METROBRAND.NS",
    "Ethos"                                : "ETHOSLTD.NS",
    "Senco Gold"                           : "SENCO.NS",
    "Kalyan Jewellers"                     : "KALYANKJIL.NS",
    "Titan Company"                        : "TITAN.NS",
    "PC Jeweller"                          : "PCJEWELLER.NS",
    "Tata Power"                           : "TATAPOWER.NS",
    "Adani Power"                          : "ADANIPOWER.NS",
    "JSW Energy"                           : "JSWENERGY.NS",
    "Torrent Power"                        : "TORNTPOWER.NS",
    "CESC"                                 : "CESC.NS",
    "PTC India"                            : "PTC.NS",
    "Suzlon Energy"                        : "SUZLON.NS",
    "Sterling and Wilson Renewable"        : "SWSOLAR.NS",
    "BHEL"                                 : "BHEL.NS",
    "Bharat Forge"                         : "BHARATFORG.NS",
    "Cummins India"                        : "CUMMINSIND.NS",
    "Thermax"                              : "THERMAX.NS",
    "Siemens India"                        : "SIEMENS.NS",
    "ABB India"                            : "ABB.NS",
    "Honeywell Automation"                 : "HONAUT.NS",
    "Schaeffler India"                     : "SCHAEFFLER.NS",
    "SKF India"                            : "SKFINDIA.NS",
    "Timken India"                         : "TIMKEN.NS",
    "Grindwell Norton"                     : "GRINDWELL.NS",
    "NOCIL"                                : "NOCIL.NS",
    "SRF"                                  : "SRF.NS",
    "Navin Fluorine International"         : "NAVINFLUOR.NS",
    "Gujarat Fluorochemicals"              : "FLUOROCHEM.NS",
    "Deepak Nitrite"                       : "DEEPAKNTR.NS",
    "Aarti Industries"                     : "AARTIIND.NS",
    "Aarti Drugs"                          : "AARTIDRUGS.NS",
    "Aarti Surfactants"                    : "AARTISURF.NS",
    "Fine Organic Industries"              : "FINEORG.NS",
    "Vinati Organics"                      : "VINATIORGA.NS",
    # ── Midcap — Finance ──────────────────────────────────────────────────────
    "Shriram Finance"                      : "SHRIRAMFIN.NS",
    "Cholamandalam Finance"                : "CHOLAFIN.NS",
    "Muthoot Finance"                      : "MUTHOOTFIN.NS",
    "AU Small Finance Bank"                : "AUBANK.NS",
    "IDFC First Bank"                      : "IDFCFIRSTB.NS",
    "Federal Bank"                         : "FEDERALBNK.NS",
    "Bank of Baroda"                       : "BANKBARODA.NS",
    "Punjab National Bank (PNB)"           : "PNB.NS",
    "Canara Bank"                          : "CANBK.NS",
    "IIFL Finance"                         : "IIFL.NS",
    "Can Fin Homes"                        : "CANFINHOME.NS",
    "Home First Finance"                   : "HOMEFIRST.NS",
    "Five Star Business Finance"           : "FIVESTAR.NS",
    "Angel One"                            : "ANGELONE.NS",
    "Motilal Oswal Financial"              : "MOTILALOFS.NS",
    "HDFC AMC"                             : "HDFCAMC.NS",
    "Nippon India AMC"                     : "NAM-INDIA.NS",
    "CAMS"                                 : "CAMS.NS",
    "CDSL"                                 : "CDSL.NS",
    "BSE Ltd"                              : "BSE.NS",
    "MCX India"                            : "MCX.NS",
    "360 One WAM"                          : "360ONE.NS",
    "Aditya Birla Capital"                 : "ABCAPITAL.NS",
    "Star Health Insurance"                : "STARHEALTH.NS",
    # ── Midcap — Real Estate & Hotels ─────────────────────────────────────────
    "DLF"                                  : "DLF.NS",
    "Godrej Properties"                    : "GODREJPROP.NS",
    "Oberoi Realty"                        : "OBEROIRLTY.NS",
    "Prestige Estates"                     : "PRESTIGE.NS",
    "Brigade Enterprises"                  : "BRIGADE.NS",
    "Phoenix Mills"                        : "PHOENIXLTD.NS",
    "Indian Hotels (Taj)"                  : "INDHOTEL.NS",
    "Lemon Tree Hotels"                    : "LEMONTREE.NS",
    "Chalet Hotels"                        : "CHALET.NS",
    # ── Midcap — Chemicals ────────────────────────────────────────────────────
    "Atul Ltd"                             : "ATUL.NS",
    "Alkyl Amines"                         : "ALKYLAMINE.NS",
    "Laxmi Organic Industries"             : "LXCHEM.NS",
    "Galaxy Surfactants"                   : "GALAXYSURF.NS",
    "Balaji Amines"                        : "BALAMINES.NS",
    "Deepak Fertilisers"                   : "DEEPAKFERT.NS",
    "Yasho Industries"                     : "YASHO.NS",
    "Tata Chemicals"                       : "TATACHEM.NS",
    "Bodal Chemicals"                      : "BODALCHEM.NS",
    # ── Midcap — Auto & Ancillaries ───────────────────────────────────────────
    "Balkrishna Industries (BKT)"          : "BALKRISIND.NS",
    "MRF"                                  : "MRF.NS",
    "CEAT Tyres"                           : "CEAT.NS",
    "Apollo Tyres"                         : "APOLLOTYRE.NS",
    "Uno Minda"                            : "UNOMINDA.NS",
    "Endurance Technologies"               : "ENDURANCE.NS",
    "Sansera Engineering"                  : "SANSERA.NS",
    "Tube Investments of India"            : "TIINDIA.NS",
    "Suprajit Engineering"                 : "SUPRAJIT.NS",
    "Craftsman Automation"                 : "CRAFTSMAN.NS",
    "Ramkrishna Forgings"                  : "RKFORGE.NS",
    # ── Midcap — Cables & Electricals ─────────────────────────────────────────
    "Polycab India"                        : "POLYCAB.NS",
    "KEI Industries"                       : "KEI.NS",
    "RR Kabel"                             : "RRKABEL.NS",
    "Finolex Cables"                       : "FINCABLES.NS",
    "APL Apollo Tubes"                     : "APLAPOLLO.NS",
    "Ratnamani Metals"                     : "RATNAMANI.NS",
    # ── Midcap — Infrastructure ───────────────────────────────────────────────
    "KEC International"                    : "KEC.NS",
    "Kalpataru Projects"                   : "KPIL.NS",
    "NCC Ltd"                              : "NCC.NS",
    "PNC Infratech"                        : "PNCINFRA.NS",
    "G R Infraprojects"                    : "GRINFRA.NS",
    "HG Infra Engineering"                 : "HGINFRA.NS",
    "Ashoka Buildcon"                      : "ASHOKA.NS",
    "PSP Projects"                         : "PSPPROJECT.NS",
    "Ahluwalia Contracts"                  : "AHLUCONT.NS",
    "RITES Ltd"                            : "RITES.NS",
    "RailTel Corporation"                  : "RAILTEL.NS",
    "IRCON International"                  : "IRCON.NS",
    "NBCC India"                           : "NBCC.NS",
    # ── Smallcap — Defence & Aerospace ───────────────────────────────────────
    "Bharat Electronics (BEL)"             : "BEL.NS",
    "Hindustan Aeronautics (HAL)"          : "HAL.NS",
    "Bharat Dynamics (BDL)"                : "BDL.NS",
    "Data Patterns India"                  : "DATAPATTNS.NS",
    "MTAR Technologies"                    : "MTARTECH.NS",
    "Paras Defence"                        : "PARAS.NS",
    "Ideaforge Technology"                 : "IDEAFORGE.NS",
    "Garden Reach Shipbuilders (GRSE)"     : "GRSE.NS",
    "Mazagon Dock Shipbuilders"            : "MAZDOCK.NS",
    "Cochin Shipyard"                      : "COCHINSHIP.NS",
    "BEML Ltd"                             : "BEML.NS",
    "Solar Industries India"               : "SOLARINDS.NS",
    "Astra Microwave Products"             : "ASTRAMICRO.NS",
    "Mishra Dhatu Nigam (Midhani)"         : "MIDHANI.NS",
    # ── Smallcap — IT & Digital ───────────────────────────────────────────────
    "Route Mobile"                         : "ROUTE.NS",
    "Tanla Platforms"                      : "TANLA.NS",
    "Nazara Technologies"                  : "NAZARA.NS",
    "Latent View Analytics"                : "LATENTVIEW.NS",
    "Rategain Travel Technologies"         : "RATEGAIN.NS",
    "HFCL Ltd"                             : "HFCL.NS",
    "Cyient Ltd"                           : "CYIENT.NS",
    "Zensar Technologies"                  : "ZENSARTECH.NS",
    "Mastek Ltd"                           : "MASTEK.NS",
    # ── Smallcap — Pharma ─────────────────────────────────────────────────────
    "Ipca Laboratories"                    : "IPCALAB.NS",
    "Ajanta Pharma"                        : "AJANTPHARM.NS",
    "JB Chemicals & Pharma"                : "JBCHEPHARM.NS",
    "Suven Pharmaceuticals"                : "SUVENPHAR.NS",
    "Gland Pharma"                         : "GLAND.NS",
    "Eris Lifesciences"                    : "ERIS.NS",
    "Indoco Remedies"                      : "INDOCO.NS",
    "Neuland Laboratories"                 : "NEULANDLAB.NS",
    "Sequent Scientific"                   : "SEQUENT.NS",
    # ── Smallcap — Chemicals ──────────────────────────────────────────────────
    "Alkyl Amines Chemicals"               : "ALKYLAMINE.NS",
    "Rossari Biotech"                      : "ROSSARI.NS",
    "Anupam Rasayan"                       : "ANURAS.NS",
    "Clean Science & Technology"           : "CLEAN.NS",
    "Neogen Chemicals"                     : "NEOGEN.NS",
    "Ami Organics"                         : "AMIORG.NS",
    # ── Smallcap — Textiles ───────────────────────────────────────────────────
    "KPR Mill"                             : "KPRMILL.NS",
    "Trident Ltd"                          : "TRIDENT.NS",
    "Indo Count Industries"                : "ICIL.NS",
    "Gokaldas Exports"                     : "GOKALDAS.NS",
    "Welspun India"                        : "WELSPUNIND.NS",
    # ── Smallcap — Agri & FMCG ───────────────────────────────────────────────
    "Avanti Feeds"                         : "AVANTIFEED.NS",
    "Zydus Wellness"                       : "ZYDUSWELL.NS",
    "Mrs Bectors Food"                     : "BECTORFOOD.NS",
    "Dodla Dairy"                          : "DODLA.NS",
    "Parag Milk Foods"                     : "PARAGMILK.NS",
}

# sorted display list: "Company Name (TICKER.NS)"
NSE_OPTIONS = sorted([f"{name}  ({ticker})" for name, ticker in NSE_STOCKS.items()])

def extract_ticker(option: str) -> str:
    """Pull ticker out of 'Company Name  (TICKER.NS)' format."""
    return option.split("(")[-1].rstrip(")")

def normalize_ticker(raw: str) -> str:
    """Uppercase, strip spaces, fix partial/mistyped exchange suffixes."""
    t = raw.upper().strip().replace(" ", "")
    if not t:
        return t
    if "." not in t:
        return t + ".NS"
    base, suffix = t.rsplit(".", 1)
    if suffix in ("NS", "BO"):
        return t
    if suffix.startswith("N"):
        return base + ".NS"
    if suffix.startswith("B"):
        return base + ".BO"
    return base + ".NS"

# ── Sidebar controls ──────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<p style='font-size:1rem;font-weight:700;margin-bottom:4px'>Settings</p>", unsafe_allow_html=True)

    ticker = "RELIANCE.NS"   # default until user picks one

    manual_raw = st.text_input(
        "Search company / ticker",
        placeholder="e.g. Deepak Nitrite, GRAVITA.NS, HDFCBANK",
    ).strip()

    # Suggestion dropdown after 3 characters
    if manual_raw and len(manual_raw) >= 3:
        query = manual_raw.upper().replace(" ", "")
        query_words = manual_raw.upper().split()
        name_words_cache = {name: name.upper().replace(" ","").replace("&","")
                            for name in NSE_STOCKS}
        def _matches(name, tkr):
            n = name_words_cache[name]
            t = tkr.upper().replace(".NS","").replace(".BO","")
            # exact substring in compact name or ticker
            if query in n or query in t:
                return True
            # all query words appear as prefixes somewhere in company name words
            name_parts = name.upper().split()
            if query_words and all(
                any(part.startswith(qw) for part in name_parts)
                for qw in query_words
            ):
                return True
            # single word prefix match
            if any(part.startswith(query[:4]) for part in name_parts):
                return True
            return False

        hits = [
            (f"{name}  ({tkr})", tkr)
            for name, tkr in NSE_STOCKS.items()
            if _matches(name, tkr)
        ][:6]
        if hits:
            choice = st.radio(
                "Suggestions",
                [lbl for lbl, _ in hits],
                index=None,
                key="sug_radio",
                label_visibility="collapsed",
            )
            if choice:
                ticker = next(t for lbl, t in hits if lbl == choice)
                st.caption(f"Selected: **{ticker}**")
            else:
                st.caption("☝️ Select a company above")
        else:
            # No suggestions — treat as a direct ticker entry
            ticker = normalize_ticker(manual_raw)
            st.caption(f"Using: **{ticker}**")
    elif manual_raw and "." in manual_raw:
        # Short input but looks like a direct ticker
        ticker = normalize_ticker(manual_raw)
        st.caption(f"Using: **{ticker}**")

    PRESETS = {
        "Swing (1–3 weeks)  ← recommended": dict(interval="1d",  period="1y",  stop=3.0, target=8.0,  vol=1.2),
        "Short Term (1–8 weeks)"           : dict(interval="1d",  period="1y",  stop=4.0, target=10.0, vol=1.1),
        "Medium Term (1–6 months)"         : dict(interval="1wk", period="2y",  stop=6.0, target=15.0, vol=1.0),
        "Intraday (same day)"              : dict(interval="15m", period="60d", stop=1.5, target=3.0,  vol=1.2),
    }
    style = st.selectbox("Trading Style", list(PRESETS.keys()), index=0)
    p     = PRESETS[style]

    interval = st.selectbox("Interval", ["1h", "1d", "1wk", "1mo", "15m"],
                            index=["1h","1d","1wk","1mo","15m"].index(p["interval"]))
    period   = st.selectbox("Period",   ["60d", "1y", "2y", "5y", "6mo", "7d"],
                            index=["60d","1y","2y","5y","6mo","7d"].index(p["period"]))

    run = st.button("▶ Run Backtest", type="primary", use_container_width=True)

    with st.expander("Risk Parameters"):
        use_atr = st.checkbox("ATR-based SL/TP (recommended)", value=True,
                              help="Stop-loss adapts to each stock's volatility")
        if use_atr:
            atr_sl_mult   = st.slider("Initial SL — ATR multiplier", min_value=0.5, max_value=3.0, value=1.5, step=0.1)
            use_trailing  = st.checkbox("Trailing stop (ride the full trend)", value=True,
                                        help="SL ratchets up as price rises — no fixed TP, exits only when trend reverses")
            if use_trailing:
                atr_trail_mult = st.slider("Trail SL — ATR multiplier", min_value=1.0, max_value=5.0, value=2.0, step=0.5)
                atr_tp_mult    = 999.0   # effectively no fixed TP
                st.caption(f"Initial SL = {atr_sl_mult}×ATR · Trail SL = {atr_trail_mult}×ATR below peak")
            else:
                atr_tp_mult    = st.slider("TP — ATR multiplier", min_value=1.0, max_value=6.0, value=2.5, step=0.5)
                atr_trail_mult = 2.0
                st.caption(f"R:R = 1 : {atr_tp_mult/atr_sl_mult:.1f}  ·  SL/TP = {atr_sl_mult}× / {atr_tp_mult}× ATR")
            stop_pct   = 0.02
            target_pct = 0.05
        else:
            stop_pct      = st.slider("Stop Loss %",   min_value=0.5, max_value=6.0,  value=p["stop"],   step=0.1) / 100
            target_pct    = st.slider("Take Profit %", min_value=1.0, max_value=15.0, value=p["target"], step=0.5) / 100
            st.caption(f"R:R = 1 : {target_pct/stop_pct:.1f}")
            atr_sl_mult   = 1.5
            atr_tp_mult   = 2.5
            atr_trail_mult = 2.0
            use_trailing  = False
        vol_mult = st.slider("Volume Filter (x avg)", min_value=1.0, max_value=2.0, value=p["vol"], step=0.1)

    with st.expander("Entry / Exit Rules"):
        st.markdown("**Entry (all timeframes)**\n"
                    "- EMA9 × EMA21 crossover (recent, within window)\n"
                    "- ADX > 25 (trending market only)\n"
                    "- Bullish/bearish candle (close > open for LONG)\n"
                    "- Price within 2% of EMA21 (pullback confirmed)\n"
                    "- RSI in range + Volume spike")
        if use_atr:
            st.markdown(f"**Exit**\n"
                        f"- Stop Loss: **{atr_sl_mult}× ATR** below entry\n"
                        f"- Take Profit: **{atr_tp_mult}× ATR** above entry\n"
                        f"- Intrabar SL/TP via candle high/low\n"
                        f"- Force exit on EMA reversal")
        else:
            st.markdown(f"**Exit**\n"
                        f"- Stop Loss: **{stop_pct*100:.1f}%**\n"
                        f"- Take Profit: **{target_pct*100:.1f}%** (R:R 1:{target_pct/stop_pct:.1f})\n"
                        f"- Intrabar SL/TP via candle high/low\n"
                        f"- Force exit on EMA reversal")

    st.caption("🔔 Hourly BUY alert runs automatically. Results appear top-right.")


# ── Indicators ────────────────────────────────────────────────────────────────

def calc_ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def calc_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def calc_bollinger(series, period=20, std=2):
    mid  = series.rolling(period).mean()
    band = series.rolling(period).std()
    return mid, mid + std * band, mid - std * band

def calc_vwap(df):
    tp  = (df["high"] + df["low"] + df["close"]) / 3
    return (tp * df["volume"]).cumsum() / df["volume"].cumsum()

def calc_adx(df, period=14):
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    dm_plus  = ((high - high.shift(1)).clip(lower=0)
                .where((high - high.shift(1)) > (low.shift(1) - low), 0))
    dm_minus = ((low.shift(1) - low).clip(lower=0)
                .where((low.shift(1) - low) > (high - high.shift(1)), 0))
    atr      = tr.ewm(span=period, adjust=False).mean()
    di_plus  = 100 * dm_plus.ewm(span=period,  adjust=False).mean() / atr
    di_minus = 100 * dm_minus.ewm(span=period, adjust=False).mean() / atr
    dx       = (100 * (di_plus - di_minus).abs() / (di_plus + di_minus).replace(0, np.nan))
    return dx.ewm(span=period, adjust=False).mean()


def calc_atr(df, period=14):
    high, low, close = df["high"], df["low"], df["close"]
    tr = pd.concat([
        high - low,
        (high - close.shift(1)).abs(),
        (low  - close.shift(1)).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(span=period, adjust=False).mean()


# ── Data + signals ────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_and_process(ticker, interval, period, vol_mult):
    try:
        raw = yf.download(ticker, interval=interval, period=period,
                          auto_adjust=True, progress=False)

        # Fallback: yf.download sometimes returns empty for certain period/interval combos
        if raw is None or raw.empty:
            raw = yf.Ticker(ticker).history(interval=interval, period=period, auto_adjust=True)

        if raw is None or raw.empty:
            return None

        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = [c[0].lower() for c in raw.columns]
        else:
            raw.columns = [c.lower() for c in raw.columns]

        # Duplicate columns = multi-ticker download (e.g. ticker had a space)
        if raw.columns.duplicated().any():
            return None
        if not all(c in raw.columns for c in ["open", "high", "low", "close", "volume"]):
            return None

        df = raw[["open", "high", "low", "close", "volume"]].dropna().copy()
        df["ema9"]    = calc_ema(df["close"], 9)
        df["ema21"]   = calc_ema(df["close"], 21)
        df["ema50"]   = calc_ema(df["close"], 50)
        df["rsi"]     = calc_rsi(df["close"], 14)
        df["adx"]     = calc_adx(df, 14)
        df["atr"]     = calc_atr(df, 14)
        df["avg_vol"] = df["volume"].rolling(20).mean()
        df["bb_mid"], df["bb_upper"], df["bb_lower"] = calc_bollinger(df["close"])
        df["vwap"]    = calc_vwap(df)

        prev9  = df["ema9"].shift(1)
        prev21 = df["ema21"].shift(1)
        bull   = (prev9 <= prev21) & (df["ema9"] > df["ema21"])
        bear   = (prev9 >= prev21) & (df["ema9"] < df["ema21"])
        vol_ok = df["volume"] >= df["avg_vol"] * vol_mult

        is_intraday = interval not in ("1d", "1wk", "1mo")
        vwap_buy  = (df["close"] > df["vwap"]) if is_intraday else True
        vwap_sell = (df["close"] < df["vwap"]) if is_intraday else True

        rsi_rising  = df["rsi"] > df["rsi"].shift(1)
        rsi_falling = df["rsi"] < df["rsi"].shift(1)

        # ── Price-Volume Action helpers ───────────────────────────────────────
        rng = (df["high"] - df["low"]).replace(0, np.nan)

        # Candle quality: close in upper 50% of range + meaningful body (not doji)
        cq_bull = (
            ((df["close"] - df["low"]) / rng > 0.50) &
            ((df["close"] - df["open"]).abs() / rng > 0.25)
        )
        cq_bear = (
            ((df["high"] - df["close"]) / rng > 0.50) &
            ((df["close"] - df["open"]).abs() / rng > 0.25)
        )

        # Relative volume
        rvol = df["volume"] / df["avg_vol"].replace(0, np.nan)

        # Volume dry-up: recent bars traded quietly (healthy pullback / base)
        vol3_avg = (df["volume"].shift(1) + df["volume"].shift(2) + df["volume"].shift(3)) / 3
        vol_dry_pullback = vol3_avg < df["avg_vol"] * 0.90

        # Volume expanding on signal bar vs. previous bar
        vol_expand = df["volume"] > df["volume"].shift(1) * 1.05

        # Tight base: 5-bar price range < 35% of 20-bar range (consolidation squeeze)
        range5  = df["high"].rolling(5).max()  - df["low"].rolling(5).min()
        range20 = df["high"].rolling(20).max() - df["low"].rolling(20).min()
        tight_base = range5 < range20 * 0.38

        # Breakout: close above highest high of last 10 bars (avoid look-ahead)
        hi10 = df["high"].rolling(10).max().shift(1)
        breakout_close = df["close"] > hi10

        def _bull_w(n):
            w = bull.copy()
            for i in range(1, n): w = w | bull.shift(i).fillna(False)
            return w & (df["ema9"] > df["ema21"])
        def _bear_w(n):
            w = bear.copy()
            for i in range(1, n): w = w | bear.shift(i).fillna(False)
            return w & (df["ema9"] < df["ema21"])

        trend_up = (df["ema9"] > df["ema21"]) & (df["ema21"] > df["ema50"])
        trend_dn = (df["ema9"] < df["ema21"]) & (df["ema21"] < df["ema50"])
        strong_up = trend_up & (df["adx"] > 25)
        strong_dn = trend_dn & (df["adx"] > 25)

        # ── Signal 1: EMA21 pullback bounce ──────────────────────────────────
        pb_buy  = (trend_up
                   & (df["low"]  <= df["ema21"] * 1.01)
                   & (df["close"] > df["ema21"])
                   & cq_bull & df["rsi"].between(35, 70) & rsi_rising
                   & (rvol > 0.8))
        pb_sell = (trend_dn
                   & (df["high"] >= df["ema21"] * 0.99)
                   & (df["close"] < df["ema21"])
                   & cq_bear & df["rsi"].between(30, 65) & rsi_falling
                   & (rvol > 0.8))

        # ── Signal 2: EMA9 pullback bounce (strong/fast trends) ──────────────
        pb9_buy  = (strong_up
                    & (df["low"]  <= df["ema9"] * 1.005)
                    & (df["close"] > df["ema9"])
                    & cq_bull & df["rsi"].between(40, 72) & rsi_rising
                    & (rvol > 0.8))
        pb9_sell = (strong_dn
                    & (df["high"] >= df["ema9"] * 0.995)
                    & (df["close"] < df["ema9"])
                    & cq_bear & df["rsi"].between(28, 60) & rsi_falling
                    & (rvol > 0.8))

        # ── Signal 3: Breakout from tight base on volume surge ────────────────
        # Stock consolidates (price coils, ATR contracts), then breaks out on 1.5x+ volume.
        # Doesn't need an EMA cross — the volume surge IS the signal.
        breakout_buy = (
            (df["ema21"] > df["ema50"]) &       # macro trend intact
            tight_base.shift(1) &               # was consolidating last bar
            breakout_close &                    # closes above 10-bar high
            (rvol > 1.5) &                      # strong volume expansion
            cq_bull &                           # quality close near high
            df["rsi"].between(45, 80) & rsi_rising &
            (df["adx"] > 15)                    # some trend/momentum
        )
        breakout_sell = (
            (df["ema21"] < df["ema50"]) &
            tight_base.shift(1) &
            (df["close"] < df["low"].rolling(10).min().shift(1)) &
            (rvol > 1.5) &
            cq_bear &
            df["rsi"].between(20, 55) & rsi_falling &
            (df["adx"] > 15)
        )

        # ── Signal 4: Volume dry-up pullback + bounce ─────────────────────────
        # In uptrend, pullback happened on quiet/declining volume (no distribution),
        # now bouncing with volume returning. EMA touch NOT required — volume pattern
        # is the signal. This catches entries before price even touches EMA21.
        vdup_buy = (
            trend_up &
            vol_dry_pullback &                  # last 3 bars were quiet
            vol_expand &                        # today volume picking up
            (df["close"] > df["ema9"]) &        # bouncing above ema9
            (df["close"] > df["open"]) &
            cq_bull &
            df["rsi"].between(40, 72) & rsi_rising
        )
        vdup_sell = (
            trend_dn &
            vol_dry_pullback &
            vol_expand &
            (df["close"] < df["ema9"]) &
            (df["close"] < df["open"]) &
            cq_bear &
            df["rsi"].between(28, 60) & rsi_falling
        )

        # ── Signal 5: Climax exhaustion (sell only) ───────────────────────────
        # After extended run above EMA21, a high-volume reversal bar signals
        # institutional distribution — good time to exit or tighten stops.
        extended = df["close"] > df["ema21"] * 1.12
        climax_sell = (
            trend_up &
            extended &
            (df["high"] > df["high"].shift(1)) &   # made new high intraday
            (df["close"] < df["open"]) &           # but closed lower (reversal)
            (rvol > 2.0) &                         # very high volume = distribution
            (df["rsi"] > 72)
        )

        # ── Signal 6: EMA9/EMA21 crossover — early trend reversal ────────────
        # Fires on the FIRST bar EMA9 crosses above EMA21 (or below for sell).
        # Catches reversals before full EMA alignment — the signal missing when
        # a stock/index bottoms and starts a new uptrend.
        xo_buy = (
            (df["ema9"] > df["ema21"]) &
            (df["ema9"].shift(1) <= df["ema21"].shift(1)) &   # just crossed up
            cq_bull &
            (rvol > 1.0) &
            df["rsi"].between(40, 78) & rsi_rising &
            (df["adx"] > 12)
        )
        xo_sell = (
            (df["ema9"] < df["ema21"]) &
            (df["ema9"].shift(1) >= df["ema21"].shift(1)) &   # just crossed down
            cq_bear &
            (rvol > 1.0) &
            df["rsi"].between(22, 60) & rsi_falling &
            (df["adx"] > 12) &
            (df["ema21"] < df["ema50"])                       # confirm bearish context
        )

        if interval == "1mo":
            cross_buy, cross_sell = _bull_w(3), _bear_w(3)
            adx_ok = df["adx"] > 20
            buy_ok  = (cross_buy  & cq_bull & df["rsi"].between(35, 70) & rsi_rising  & (df["close"] > df["ema50"]) & adx_ok) | pb_buy | pb9_buy | breakout_buy | vdup_buy | xo_buy
            sell_ok = (cross_sell & cq_bear & df["rsi"].between(30, 65) & rsi_falling & (df["close"] < df["ema50"]) & (df["ema21"] < df["ema50"]) & adx_ok) | pb_sell | pb9_sell | breakout_sell | climax_sell | xo_sell
        elif interval == "1wk":
            cross_buy, cross_sell = _bull_w(4), _bear_w(4)
            adx_ok = df["adx"] > 20
            buy_ok  = (cross_buy  & cq_bull & df["rsi"].between(40, 72) & rsi_rising  & (rvol > 1.0) & (df["close"] > df["ema50"]) & adx_ok) | pb_buy | pb9_buy | breakout_buy | vdup_buy | xo_buy
            sell_ok = (cross_sell & cq_bear & df["rsi"].between(28, 58) & rsi_falling & (rvol > 1.0) & (df["close"] < df["ema50"]) & (df["ema21"] < df["ema50"]) & adx_ok) | pb_sell | pb9_sell | breakout_sell | climax_sell | xo_sell
        elif interval == "1d":
            cross_buy, cross_sell = _bull_w(5), _bear_w(5)
            adx_ok = df["adx"] > 20
            buy_ok  = (cross_buy  & cq_bull & df["rsi"].between(45, 75) & rsi_rising  & vol_ok & (df["close"] > df["ema50"]) & adx_ok) | pb_buy | pb9_buy | breakout_buy | vdup_buy | xo_buy
            sell_ok = (cross_sell & cq_bear & df["rsi"].between(25, 55) & rsi_falling & vol_ok & (df["close"] < df["ema50"]) & (df["ema21"] < df["ema50"]) & adx_ok) | pb_sell | pb9_sell | breakout_sell | climax_sell | xo_sell
        else:
            adx_ok = df["adx"] > 25
            buy_ok  = (bull & cq_bull & df["rsi"].between(45, 75) & vol_ok & (df["close"] > df["ema50"]) & vwap_buy  & adx_ok) | pb9_buy | vdup_buy | xo_buy
            sell_ok = (bear & cq_bear & df["rsi"].between(25, 55) & vol_ok & (df["close"] < df["ema50"]) & (df["ema21"] < df["ema50"]) & vwap_sell & adx_ok) | pb9_sell | climax_sell | xo_sell

        df["signal"] = 0
        df["sig_type"] = ""
        df.loc[buy_ok,  "signal"] =  1
        df.loc[sell_ok, "signal"] = -1
        # Label signal types (priority: most specific first)
        df.loc[xo_buy,        "sig_type"] = "XO"     # EMA crossover reversal
        df.loc[xo_sell,       "sig_type"] = "XO"
        df.loc[breakout_buy,  "sig_type"] = "BO"     # Breakout
        df.loc[vdup_buy,      "sig_type"] = "VD"     # Vol dry-up pullback
        df.loc[pb9_buy,       "sig_type"] = "PB9"    # EMA9 pullback
        df.loc[pb_buy,        "sig_type"] = "PB21"   # EMA21 pullback
        df.loc[breakout_sell, "sig_type"] = "BO"
        df.loc[climax_sell,   "sig_type"] = "CLX"    # Climax/exhaustion
        df.loc[pb9_sell,      "sig_type"] = "PB9"
        df.loc[pb_sell,       "sig_type"] = "PB21"
        return df

    except Exception:
        return None


def run_backtest(df, stop_pct, target_pct, use_atr=True, atr_sl_mult=1.5, atr_tp_mult=2.5,
                 use_trailing=True, atr_trail_mult=2.0):
    trades   = []
    position = None

    for ts, row in df.iterrows():
        if position is not None:
            side  = position["side"]
            hi    = float(row["high"])
            lo    = float(row["low"])
            close = float(row["close"])
            atr   = float(row["atr"]) if "atr" in row and not np.isnan(float(row["atr"])) else None

            # Update trailing stop: ratchet SL up (long) or down (short) as price moves
            if use_trailing and atr is not None:
                new_peak = max(position["peak"], hi) if side == 1 else min(position["peak"], lo)
                position["peak"] = new_peak
                trail_sl = new_peak - side * atr_trail_mult * atr
                # Only move SL in the profitable direction
                if side == 1 and trail_sl > position["sl"]:
                    position["sl"] = trail_sl
                elif side == -1 and trail_sl < position["sl"]:
                    position["sl"] = trail_sl

            sl = position["sl"]
            tp = position["tp"]

            # Intrabar check via candle high/low
            hit_sl = (side ==  1 and lo  <= sl) or (side == -1 and hi  >= sl)
            hit_tp = (side ==  1 and hi  >= tp) or (side == -1 and lo  <= tp)
            if hit_sl and hit_tp:
                hit_tp = False   # SL wins if both triggered same candle

            if hit_tp or hit_sl:
                exit_p = tp if hit_tp else sl
                pnl    = side * (exit_p - position["entry"]) / position["entry"] * 100
                is_trail = hit_sl and use_trailing and (
                    (side == 1 and position["sl"] > position["initial_sl"]) or
                    (side == -1 and position["sl"] < position["initial_sl"])
                )
                reason = "TP" if hit_tp else ("Trail SL" if is_trail else "SL")
                # Store initial_sl for chart display; mark tp as NaN when trailing (no fixed TP)
                display_tp = np.nan if use_trailing else round(tp, 4)
                trades.append({
                    "entry_time": position["entry_time"],
                    "exit_time" : ts,
                    "side"      : "LONG" if side == 1 else "SHORT",
                    "entry"     : round(position["entry"], 4),
                    "exit"      : round(exit_p, 4),
                    "pnl_%"     : round(pnl, 3),
                    "reason"    : reason,
                    "sl"        : round(position["initial_sl"], 4),  # initial SL for chart box
                    "tp"        : display_tp,
                })
                position = None

        if position is None and row["signal"] != 0:
            entry = float(row["close"])
            side  = int(row["signal"])
            atr   = float(row["atr"]) if "atr" in row and not np.isnan(float(row["atr"])) else np.nan

            if use_atr and not np.isnan(atr):
                sl = entry - side * atr_sl_mult * atr
                tp = entry + side * atr_tp_mult * atr
            else:
                sl = entry * (1 - side * stop_pct)
                tp = entry * (1 + side * target_pct)

            position = {
                "side": side, "entry": entry, "entry_time": ts,
                "sl": sl, "tp": tp, "initial_sl": sl,
                "peak": entry,   # tracks highest high (long) or lowest low (short)
            }

    return pd.DataFrame(trades) if trades else pd.DataFrame()


# ── Chart builder ─────────────────────────────────────────────────────────────

def build_chart(df, trades_df, ticker, interval, stop_pct, target_pct):
    # For intraday: use string labels as x-axis to eliminate all gaps
    if interval == "1mo":
        x_vals = df.index
    elif interval in ("1d", "1wk"):
        x_vals = df.index
    else:
        x_vals = df.index.strftime("%b %d  %H:%M")

    has_trades = not trades_df.empty

    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        row_heights=[0.50, 0.18, 0.13, 0.19],
        vertical_spacing=0.02,
        subplot_titles=(
            f"{ticker}  ·  {interval}  —  Price · EMA · Bollinger" + ("" if interval in ("1d","1wk","1mo") else " · VWAP"),
            "RSI (14)",
            "Volume",
            "Equity Curve  (Cumulative P&L %)",
        ),
    )

    # ── Timestamp → x-label mapper ────────────────────────────────────────────
    if interval not in ("1d", "1wk", "1mo"):
        ts_to_x = {ts: lbl for ts, lbl in zip(df.index, x_vals)}
        def _tx(ts):
            if ts in ts_to_x:
                return ts_to_x[ts]
            nearest = min(df.index, key=lambda t: abs(t - ts))
            return ts_to_x[nearest]
    else:
        def _tx(ts): return ts

    # ── 1. Bollinger Band fill ─────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["bb_upper"], name="BB Upper",
        line=dict(color="rgba(148,163,184,0.3)", width=1),
        showlegend=False, hoverinfo="skip",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["bb_lower"], name="BB Band",
        line=dict(color="rgba(148,163,184,0.3)", width=1),
        fill="tonexty", fillcolor="rgba(148,163,184,0.07)",
        showlegend=True, hoverinfo="skip",
    ), row=1, col=1)

    # ── 2. R:R boxes (drawn before candles so they sit behind) ────────────────
    if has_trades:
        for _, t in trades_df.iterrows():
            is_long  = t["side"] == "LONG"
            ep       = t["entry"]
            sl_p     = float(t["sl"]) if "sl" in t and not np.isnan(float(t["sl"])) else ep * (1 - (1 if is_long else -1) * stop_pct)
            raw_tp   = t.get("tp", np.nan)
            tp_p     = float(raw_tp) if not (raw_tp != raw_tp or raw_tp is None) else None  # NaN check
            ex, xx   = _tx(t["entry_time"]), _tx(t["exit_time"])

            # SL zone — red fill between entry and initial SL
            y0, y1 = min(ep, sl_p), max(ep, sl_p)
            fig.add_trace(go.Scatter(
                x=[ex, xx, xx, ex, ex], y=[y0, y0, y1, y1, y0],
                fill="toself", fillcolor="rgba(239,83,80,0.12)",
                line=dict(width=0), showlegend=False, hoverinfo="skip",
            ), row=1, col=1)

            # TP zone — only draw when a fixed TP exists (not trailing mode)
            if tp_p is not None:
                y0, y1 = min(ep, tp_p), max(ep, tp_p)
                fig.add_trace(go.Scatter(
                    x=[ex, xx, xx, ex, ex], y=[y0, y0, y1, y1, y0],
                    fill="toself", fillcolor="rgba(34,197,94,0.09)",
                    line=dict(width=0), showlegend=False, hoverinfo="skip",
                ), row=1, col=1)

    # ── 3. Candlesticks ────────────────────────────────────────────────────────
    fig.add_trace(go.Candlestick(
        x=x_vals,
        open=df["open"], high=df["high"],
        low=df["low"],   close=df["close"],
        name="Price",
        increasing=dict(line=dict(color="#26a69a", width=1), fillcolor="#26a69a"),
        decreasing=dict(line=dict(color="#ef5350", width=1), fillcolor="#ef5350"),
        showlegend=False,
        hovertext=[
            f"O: {o:.2f}  H: {h:.2f}  L: {l:.2f}  C: {c:.2f}"
            for o, h, l, c in zip(df["open"], df["high"], df["low"], df["close"])
        ],
        hoverinfo="text+x",
    ), row=1, col=1)

    # ── 4. EMA lines ───────────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["ema9"], name="EMA 9",
        line=dict(color="#f59e0b", width=1.8),
        hovertemplate="EMA9: %{y:.2f}<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["ema21"], name="EMA 21",
        line=dict(color="#818cf8", width=1.8),
        hovertemplate="EMA21: %{y:.2f}<extra></extra>",
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["ema50"], name="EMA 50",
        line=dict(color="#34d399", width=1.4, dash="dash"),
        hovertemplate="EMA50: %{y:.2f}<extra></extra>",
    ), row=1, col=1)

    # ── 5. VWAP (intraday only) ────────────────────────────────────────────────
    if interval not in ("1d", "1wk", "1mo"):
        fig.add_trace(go.Scatter(
            x=x_vals, y=df["vwap"], name="VWAP",
            line=dict(color="#f472b6", width=1.4, dash="dot"),
            hovertemplate="VWAP: %{y:.2f}<extra></extra>",
        ), row=1, col=1)

    # ── 6. Trade overlays ─────────────────────────────────────────────────────
    if has_trades:
        # 6a. Trade path lines + SL/TP level lines (colored by win/loss)
        for _, t in trades_df.iterrows():
            is_win  = t["pnl_%"] > 0
            is_long = t["side"] == "LONG"
            clr     = "#22c55e" if is_win else "#ef5350"
            ep      = t["entry"]
            sl_p    = float(t["sl"]) if "sl" in t and not np.isnan(float(t["sl"])) else ep * (1 - (1 if is_long else -1) * stop_pct)
            raw_tp  = t.get("tp", np.nan)
            tp_p    = float(raw_tp) if not (raw_tp != raw_tp or raw_tp is None) else None
            ex, xx  = _tx(t["entry_time"]), _tx(t["exit_time"])

            fig.add_trace(go.Scatter(
                x=[ex, xx], y=[t["entry"], t["exit"]],
                mode="lines", line=dict(color=clr, width=2, dash="dot"),
                showlegend=False, hoverinfo="skip",
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=[ex, xx], y=[sl_p, sl_p],
                mode="lines", line=dict(color="#ef5350", width=1, dash="dash"),
                showlegend=False, hoverinfo="skip",
            ), row=1, col=1)
            if tp_p is not None:
                fig.add_trace(go.Scatter(
                    x=[ex, xx], y=[tp_p, tp_p],
                    mode="lines", line=dict(color="#22c55e", width=1, dash="dash"),
                    showlegend=False, hoverinfo="skip",
                ), row=1, col=1)

        # 6b. Entry markers (larger, bolder)
        longs  = trades_df[trades_df["side"] == "LONG"]
        shorts = trades_df[trades_df["side"] == "SHORT"]
        if not longs.empty:
            fig.add_trace(go.Scatter(
                x=[_tx(t) for t in longs["entry_time"]], y=longs["entry"],
                mode="markers", name="Buy Entry",
                marker=dict(symbol="triangle-up", size=16, color="#26a69a",
                            line=dict(color="white", width=1.5)),
                hovertemplate="BUY @ ₹%{y:.2f}<br>%{x}<extra></extra>",
            ), row=1, col=1)
        if not shorts.empty:
            fig.add_trace(go.Scatter(
                x=[_tx(t) for t in shorts["entry_time"]], y=shorts["entry"],
                mode="markers", name="Sell Entry",
                marker=dict(symbol="triangle-down", size=16, color="#ef5350",
                            line=dict(color="white", width=1.5)),
                hovertemplate="SELL @ ₹%{y:.2f}<br>%{x}<extra></extra>",
            ), row=1, col=1)

        # 6c. Exit markers + P&L labels (alternating top/bottom to avoid overlap)
        sorted_t = trades_df.sort_values("exit_time").reset_index(drop=True)
        last_x, flip = None, False
        for _, t in sorted_t.iterrows():
            is_win = t["pnl_%"] > 0
            clr    = "#22c55e" if is_win else "#ef5350"
            sym    = "circle" if is_win else "x"
            ex     = _tx(t["exit_time"])
            flip   = (not flip) if ex == last_x else False
            last_x = ex
            label  = f"{t['pnl_%']:+.1f}%"
            fig.add_trace(go.Scatter(
                x=[ex], y=[t["exit"]],
                mode="markers+text",
                marker=dict(symbol=sym, size=12, color=clr,
                            line=dict(color="white", width=1.5)),
                text=[label],
                textposition="bottom center" if flip else "top center",
                textfont=dict(size=9, color=clr),
                showlegend=False,
                hovertemplate=(f"{t['side']}  Exit @ ₹{t['exit']:.2f}<br>"
                               f"P&L: {label}  [{t['reason']}]<extra></extra>"),
            ), row=1, col=1)

        # 6d. Win/Loss summary box (top-right of chart)
        wins     = int((trades_df["pnl_%"] > 0).sum())
        losses   = int((trades_df["pnl_%"] <= 0).sum())
        wr       = wins / len(trades_df) * 100
        net      = trades_df["pnl_%"].sum()
        net_clr  = "#22c55e" if net >= 0 else "#ef5350"
        fig.add_annotation(
            text=f"W {wins}  L {losses}  |  WR {wr:.0f}%  |  Net <b>{net:+.1f}%</b>",
            xref="paper", yref="paper",
            x=0.99, y=0.99, xanchor="right", yanchor="top",
            showarrow=False,
            bgcolor="#1e293b", bordercolor="#334155", borderwidth=1,
            font=dict(size=11, color=net_clr),
        )

    # ── 6e. Raw signal markers from df (all signals, labeled by type) ─────────
    if "signal" in df.columns and "sig_type" in df.columns:
        sig_col = "sig_type" if "sig_type" in df.columns else None
        buy_rows  = df[df["signal"] ==  1]
        sell_rows = df[df["signal"] == -1]
        if not buy_rows.empty:
            bx = [_tx(t) for t in buy_rows.index]
            by = buy_rows["low"] * 0.993
            bt = buy_rows["sig_type"].tolist() if sig_col else ["B"] * len(buy_rows)
            fig.add_trace(go.Scatter(
                x=bx, y=list(by),
                mode="markers+text",
                marker=dict(symbol="triangle-up", size=11, color="rgba(38,166,154,0.85)",
                            line=dict(color="#1a8f87", width=1)),
                text=bt,
                textposition="bottom center",
                textfont=dict(size=8, color="#26a69a"),
                name="Buy Signal", showlegend=True,
                hovertemplate="BUY [%{text}] @ ₹%{customdata:.2f}<extra></extra>",
                customdata=list(buy_rows["close"]),
            ), row=1, col=1)
        if not sell_rows.empty:
            sx = [_tx(t) for t in sell_rows.index]
            sy = sell_rows["high"] * 1.007
            st = sell_rows["sig_type"].tolist() if sig_col else ["S"] * len(sell_rows)
            fig.add_trace(go.Scatter(
                x=sx, y=list(sy),
                mode="markers+text",
                marker=dict(symbol="triangle-down", size=11, color="rgba(239,83,80,0.85)",
                            line=dict(color="#c62828", width=1)),
                text=st,
                textposition="top center",
                textfont=dict(size=8, color="#ef5350"),
                name="Sell Signal", showlegend=True,
                hovertemplate="SELL [%{text}] @ ₹%{customdata:.2f}<extra></extra>",
                customdata=list(sell_rows["close"]),
            ), row=1, col=1)

    # ── 7. RSI with fill ───────────────────────────────────────────────────────
    fig.add_trace(go.Scatter(
        x=x_vals, y=[50] * len(df),
        line=dict(color="rgba(0,0,0,0)", width=0),
        showlegend=False, hoverinfo="skip",
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["rsi"], name="RSI",
        line=dict(color="#a78bfa", width=1.8),
        fill="tonexty", fillcolor="rgba(167,139,250,0.12)",
        hovertemplate="RSI: %{y:.1f}<extra></extra>",
        showlegend=False,
    ), row=2, col=1)
    for level, color, label in [(70, "#ef5350", "OB 70"), (50, "#94a3b8", "50"), (30, "#26a69a", "OS 30")]:
        fig.add_hline(y=level, line_dash="dot", line_color=color, line_width=1, row=2, col=1)
        fig.add_annotation(x=x_vals[-1], y=level, text=label,
                           xanchor="left", font=dict(size=9, color=color),
                           showarrow=False, row=2, col=1)

    # ── 8. Volume bars ─────────────────────────────────────────────────────────
    vol_colors = ["#26a69a" if c >= o else "#ef5350"
                  for c, o in zip(df["close"], df["open"])]
    fig.add_trace(go.Bar(
        x=x_vals, y=df["volume"],
        marker_color=vol_colors, opacity=0.6,
        showlegend=False,
        hovertemplate="Vol: %{y:,.0f}<extra></extra>",
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=x_vals, y=df["avg_vol"], name="Avg Vol",
        line=dict(color="#f59e0b", width=1.2, dash="dot"),
        showlegend=False,
        hovertemplate="Avg Vol: %{y:,.0f}<extra></extra>",
    ), row=3, col=1)

    # ── 9. Equity curve ────────────────────────────────────────────────────────
    if has_trades:
        eq        = trades_df.sort_values("exit_time").copy()
        eq["cum"] = eq["pnl_%"].cumsum()
        eq_x      = [_tx(ts) for ts in eq["exit_time"]]
        eq_y      = eq["cum"].tolist()
        origin_x  = _tx(eq.iloc[0]["entry_time"])
        final     = eq["cum"].iloc[-1]
        ec        = "#22c55e" if final >= 0 else "#ef5350"
        ec_fill   = "rgba(34,197,94,0.12)" if final >= 0 else "rgba(239,83,80,0.12)"
        pt_colors = ["#22c55e" if v >= 0 else "#ef5350" for v in [0.0] + eq_y]

        fig.add_trace(go.Scatter(
            x=[origin_x] + eq_x, y=[0.0] + eq_y,
            mode="lines+markers", name="Equity",
            line=dict(color=ec, width=2),
            marker=dict(size=6, color=pt_colors, line=dict(color="white", width=1)),
            fill="tozeroy", fillcolor=ec_fill,
            hovertemplate="Cum P&L: %{y:+.2f}%<extra></extra>",
        ), row=4, col=1)
        fig.add_hline(y=0, line_dash="dot", line_color="#475569", line_width=1, row=4, col=1)

    # ── Layout ─────────────────────────────────────────────────────────────────
    fig.update_layout(
        height=660,
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0", family="Inter, sans-serif", size=12),
        legend=dict(
            bgcolor="#1e293b", bordercolor="#334155", borderwidth=1,
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=11),
        ),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#1e293b", bordercolor="#334155",
                        font=dict(color="#e2e8f0", size=11)),
        margin=dict(l=10, r=60, t=60, b=10),
        xaxis4=dict(
            rangeselector=dict(
                buttons=[
                    dict(count=1,  label="1D",  step="day",   stepmode="backward"),
                    dict(count=5,  label="5D",  step="day",   stepmode="backward"),
                    dict(count=10, label="10D", step="day",   stepmode="backward"),
                    dict(count=1,  label="1M",  step="month", stepmode="backward"),
                    dict(step="all", label="All"),
                ],
                bgcolor="#1e293b", activecolor="#3b82f6",
                font=dict(color="#e2e8f0", size=11),
            ),
        ),
    )
    for i in range(1, 5):
        fig.update_xaxes(gridcolor="#1e293b", zeroline=False, row=i, col=1)
        fig.update_yaxes(gridcolor="#1e293b", zeroline=False,
                         tickprefix="₹" if i == 1 else "", row=i, col=1)
    fig.update_yaxes(tickprefix="", ticksuffix="", row=2, col=1)
    fig.update_yaxes(tickprefix="", ticksuffix="", row=3, col=1)
    fig.update_yaxes(tickprefix="", ticksuffix="%", row=4, col=1)

    if interval == "1d":
        fig.update_xaxes(rangebreaks=[dict(bounds=["sat", "mon"])])

    return fig


# ── Live signal helper ────────────────────────────────────────────────────────

def get_live_signal(df, interval="1h"):
    """Check the latest bar and return signal details."""
    last  = df.iloc[-1]
    prev  = df.iloc[-2]
    price = float(last["close"])

    ema9_now,  ema21_now  = float(last["ema9"]),  float(last["ema21"])
    ema9_prev, ema21_prev = float(prev["ema9"]),  float(prev["ema21"])
    ema50_now  = float(last["ema50"])
    rsi_val    = float(last["rsi"])
    rsi_prev   = float(prev["rsi"])
    adx_val    = float(last["adx"]) if not np.isnan(last["adx"]) else 0
    vol_now    = float(last["volume"])
    avg_vol    = float(last["avg_vol"]) if not np.isnan(last["avg_vol"]) else vol_now
    vwap_now   = float(last["vwap"])

    bull_cross  = ema9_prev <= ema21_prev and ema9_now > ema21_now
    bear_cross  = ema9_prev >= ema21_prev and ema9_now < ema21_now
    trend_up    = price > ema50_now
    trend_dn    = price < ema50_now
    above_vwap  = True if interval in ("1d","1wk","1mo") else price > vwap_now
    adx_ok      = adx_val > 20
    rsi_rising  = rsi_val > rsi_prev
    rsi_falling = rsi_val < rsi_prev

    # XO (crossover) — fires even without full EMA alignment, catches reversals
    xo_buy_ok  = bull_cross and (40 <= rsi_val <= 78) and rsi_rising  and vol_now >= avg_vol * 1.0 and adx_val > 12
    xo_sell_ok = bear_cross and (22 <= rsi_val <= 60) and rsi_falling and vol_now >= avg_vol * 1.0 and adx_val > 12 and ema9_now < ema21_now and ema21_now < ema50_now

    def _window(n):
        if len(df) < n + 1:
            return bull_cross
        bars = df.iloc[-(n+1):-1]
        p9, p21 = bars["ema9"].shift(1), bars["ema21"].shift(1)
        return (bool(((p9 <= p21) & (bars["ema9"] > bars["ema21"])).any()) or bull_cross) and ema9_now > ema21_now

    def _window_bear(n):
        if len(df) < n + 1:
            return bear_cross
        bars = df.iloc[-(n+1):-1]
        p9, p21 = bars["ema9"].shift(1), bars["ema21"].shift(1)
        return (bool(((p9 >= p21) & (bars["ema9"] < bars["ema21"])).any()) or bear_cross) and ema9_now < ema21_now

    if interval == "1mo":
        rsi_buy_ok  = 35 <= rsi_val <= 70
        rsi_sell_ok = 30 <= rsi_val <= 65
        cross_buy, cross_sell = _window(3), _window_bear(3)
        vol_check   = True
        cross_label = "EMA crossover within last 3 months"
        cond_extra_label, cond_extra = "RSI rising (momentum)", rsi_rising
        buy_confirmed  = cross_buy  and rsi_buy_ok  and rsi_rising  and trend_up or xo_buy_ok
        sell_confirmed = cross_sell and rsi_sell_ok and rsi_falling and trend_dn or xo_sell_ok

    elif interval == "1wk":
        rsi_buy_ok  = 40 <= rsi_val <= 72
        rsi_sell_ok = 28 <= rsi_val <= 58
        cross_buy, cross_sell = _window(4), _window_bear(4)
        vol_check   = vol_now >= avg_vol * 1.1
        cross_label = "EMA crossover within last 4 weeks"
        cond_extra_label, cond_extra = "RSI rising (momentum)", rsi_rising
        buy_confirmed  = cross_buy  and rsi_buy_ok  and rsi_rising  and vol_check and trend_up or xo_buy_ok
        sell_confirmed = cross_sell and rsi_sell_ok and rsi_falling and vol_check and trend_dn or xo_sell_ok

    elif interval == "1d":
        rsi_buy_ok  = 45 <= rsi_val <= 75
        rsi_sell_ok = 25 <= rsi_val <= 55
        cross_buy, cross_sell = _window(5), _window_bear(5)
        vol_check   = vol_now >= avg_vol * 1.2
        cross_label = "EMA crossover within last 5 days"
        cond_extra_label, cond_extra = "RSI rising (momentum)", rsi_rising
        buy_confirmed  = cross_buy  and rsi_buy_ok  and rsi_rising  and vol_check and trend_up or xo_buy_ok
        sell_confirmed = cross_sell and rsi_sell_ok and rsi_falling and vol_check and trend_dn or xo_sell_ok

    else:
        rsi_buy_ok  = 45 <= rsi_val <= 75
        rsi_sell_ok = 25 <= rsi_val <= 55
        cross_buy, cross_sell = bull_cross, bear_cross
        vol_check   = vol_now >= avg_vol * 1.2
        cross_label = "EMA crossover just fired"
        cond_extra_label, cond_extra = "Price above VWAP (insti. buying)", above_vwap
        buy_confirmed  = bull_cross and rsi_buy_ok  and vol_check and trend_up and above_vwap and adx_ok
        sell_confirmed = bear_cross and rsi_sell_ok and vol_check and trend_dn and not above_vwap and adx_ok

    conditions = {
        "EMA9 > EMA21 (short-term uptrend)"  : ema9_now > ema21_now,
        "EMA9 < EMA21 (short-term downtrend)": ema9_now < ema21_now,
        cross_label                           : cross_buy or cross_sell,
        "Price above EMA50 (macro uptrend)"  : trend_up,
        cond_extra_label                     : cond_extra,
        "RSI in buy zone"                    : rsi_buy_ok,
        "Volume confirmed"                   : vol_check,
        "ADX > 20 (trending market)"         : adx_ok,
    }

    buy_score  = sum([cross_buy,  rsi_buy_ok,  vol_check, trend_up,     cond_extra])
    sell_score = sum([cross_sell, rsi_sell_ok, vol_check, trend_dn, not cond_extra])

    if buy_confirmed:
        signal = "🟢 BUY"
    elif sell_confirmed:
        signal = "🔴 SELL"
    elif cross_buy or (ema9_now > ema21_now and buy_score >= 4):
        signal = "👀 Watch — Bullish"
    elif cross_sell or (ema9_now < ema21_now and sell_score >= 4):
        signal = "👀 Watch — Bearish"
    else:
        signal = "⏸ Hold"

    return signal, price, rsi_val, ema9_now, ema21_now, vol_now, avg_vol, conditions


# ── Main app ──────────────────────────────────────────────────────────────────

if "chart_ticker_override" in st.session_state:
    ticker = st.session_state.pop("chart_ticker_override")

if run or "df" not in st.session_state or ticker != st.session_state.get("ticker") or interval != st.session_state.get("interval") or period != st.session_state.get("period"):
    with st.spinner(f"Fetching {ticker} data..."):
        df = fetch_and_process(ticker, interval, period, vol_mult)

    if df is None or df.empty:
        st.error(f"Could not fetch data for **{ticker}**. The ticker may be delisted, unavailable on yfinance, or misspelled. Try adding **.NS** (NSE) or **.BO** (BSE).")
        st.stop()

    trades_df = run_backtest(df, stop_pct, target_pct, use_atr, atr_sl_mult, atr_tp_mult,
                             use_trailing, atr_trail_mult)
    st.session_state["df"]        = df
    st.session_state["trades_df"] = trades_df
    st.session_state["ticker"]    = ticker
    st.session_state["interval"]  = interval
    st.session_state["period"]    = period

df        = st.session_state.get("df")
trades_df = st.session_state.get("trades_df", pd.DataFrame())
cur_tick  = st.session_state.get("ticker", ticker)
cur_int   = st.session_state.get("interval", interval)

# ── Tab navigation ────────────────────────────────────────────────────────────
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "📊  Chart & Backtest"

page = st.session_state["active_page"]

_TABS = ["📊  Chart & Backtest", "🔍  Stock Scanner"]
_tab_css = """
<style>
.tab-bar button {
    background: none; border: none; padding: 8px 24px;
    font-size: 0.92rem; font-weight: 500; cursor: pointer;
    color: #64748b; border-bottom: 3px solid transparent;
    border-radius: 0; margin-bottom: -1px;
}
.tab-bar button.active {
    color: #2563eb; border-bottom: 3px solid #2563eb; font-weight: 700;
}
.tab-bar { border-bottom: 1px solid #e2e8f0; margin-bottom: 12px; }
</style>
"""
st.markdown(_tab_css, unsafe_allow_html=True)

t1, t2, *_ = st.columns([1.6, 1.6, 6])
with t1:
    if st.button("📊  Chart & Backtest",
                 type="primary" if page == "📊  Chart & Backtest" else "secondary",
                 use_container_width=True):
        st.session_state["active_page"] = "📊  Chart & Backtest"
        st.rerun()
with t2:
    if st.button("🔍  Stock Scanner",
                 type="primary" if page == "🔍  Stock Scanner" else "secondary",
                 use_container_width=True):
        st.session_state["active_page"] = "🔍  Stock Scanner"
        st.rerun()

# ── Scan groups (module-level so AUTO_SCAN_TICKERS can reference them) ─────────
SCAN_GROUPS = {
    # ── Nifty 50 — all 50 constituents ────────────────────────────────────────
    "Nifty 50"                      : ["RELIANCE.NS","TCS.NS","INFY.NS","HDFCBANK.NS","ICICIBANK.NS",
                                        "WIPRO.NS","HCLTECH.NS","AXISBANK.NS","SBIN.NS","KOTAKBANK.NS",
                                        "BAJFINANCE.NS","BAJAJFINSV.NS","MARUTI.NS","ASIANPAINT.NS",
                                        "HINDUNILVR.NS","LT.NS","SUNPHARMA.NS","TATAMOTORS.NS",
                                        "TATASTEEL.NS","POWERGRID.NS","NTPC.NS","ONGC.NS",
                                        "BHARTIARTL.NS","ITC.NS","NESTLEIND.NS","DRREDDY.NS",
                                        "CIPLA.NS","EICHERMOT.NS","HEROMOTOCO.NS","JSWSTEEL.NS",
                                        "HINDALCO.NS","ADANIPORTS.NS","ULTRACEMCO.NS","TITAN.NS",
                                        "TECHM.NS","INDUSINDBK.NS","COALINDIA.NS","GRASIM.NS",
                                        "BRITANNIA.NS","BAJAJ-AUTO.NS",
                                        "M&M.NS","HDFCLIFE.NS","SBILIFE.NS","APOLLOHOSP.NS",
                                        "TATACONSUM.NS","BPCL.NS","ADANIENT.NS","BEL.NS",
                                        "SHRIRAMFIN.NS","ZOMATO.NS"],
    # ── Midcap ─────────────────────────────────────────────────────────────────
    "Midcap — Finance & Banking"  : ["SHRIRAMFIN.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","AUBANK.NS",
                                      "IDFCFIRSTB.NS","FEDERALBNK.NS","BANKBARODA.NS","PNB.NS",
                                      "CANBK.NS","IIFL.NS","CANFINHOME.NS","HOMEFIRST.NS",
                                      "FIVESTAR.NS","ANGELONE.NS","MOTILALOFS.NS","HDFCAMC.NS",
                                      "NAM-INDIA.NS","CAMS.NS","CDSL.NS","BSE.NS","MCX.NS",
                                      "360ONE.NS","ABCAPITAL.NS","STARHEALTH.NS"],
    "Midcap — IT & Tech"          : ["PERSISTENT.NS","MPHASIS.NS","COFORGE.NS","LTIM.NS",
                                      "TATAELXSI.NS","KPITTECH.NS","HAPPSTMNDS.NS","BIRLASOFT.NS",
                                      "CYIENT.NS","ZENSARTECH.NS","MASTEK.NS","ROUTE.NS",
                                      "TANLA.NS","RATEGAIN.NS","LATENTVIEW.NS"],
    "Midcap — Auto & Ancillaries" : ["BALKRISIND.NS","MRF.NS","CEAT.NS","APOLLOTYRE.NS",
                                      "UNOMINDA.NS","ENDURANCE.NS","SANSERA.NS","TIINDIA.NS",
                                      "SUPRAJIT.NS","CRAFTSMAN.NS","RKFORGE.NS"],
    "Midcap — Chemicals"          : ["SRF.NS","NAVINFLUOR.NS","FLUOROCHEM.NS","DEEPAKNTR.NS",
                                      "AARTIIND.NS","FINEORG.NS","VINATIORGA.NS","ATUL.NS",
                                      "ALKYLAMINE.NS","LXCHEM.NS","GALAXYSURF.NS","BALAMINES.NS",
                                      "DEEPAKFERT.NS","TATACHEM.NS"],
    "Midcap — Infra & Real Estate": ["DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS",
                                      "BRIGADE.NS","PHOENIXLTD.NS","KEC.NS","KPIL.NS",
                                      "NCC.NS","PNCINFRA.NS","GRINFRA.NS","HGINFRA.NS",
                                      "ASHOKA.NS","RITES.NS","RAILTEL.NS","IRCON.NS","NBCC.NS"],
    "Midcap — Cables & Electricals": ["POLYCAB.NS","KEI.NS","RRKABEL.NS","FINCABLES.NS",
                                       "APLAPOLLO.NS","RATNAMANI.NS","HAVELLS.NS","CROMPTON.NS",
                                       "VOLTAS.NS"],
    # ── Smallcap ───────────────────────────────────────────────────────────────
    "Smallcap — Defence & Aerospace": ["BEL.NS","HAL.NS","BDL.NS","DATAPATTNS.NS","MTARTECH.NS",
                                        "PARAS.NS","IDEAFORGE.NS","GRSE.NS","MAZDOCK.NS",
                                        "COCHINSHIP.NS","BEML.NS","SOLARINDS.NS","ASTRAMICRO.NS",
                                        "MIDHANI.NS"],
    "Smallcap — Electronics & EMS"  : ["SYRMA.NS","KAYNES.NS","DIXON.NS","AMBER.NS",
                                        "AVALON.NS","ELIN.NS","HFCL.NS"],
    "Smallcap — IT & Digital"       : ["NAZARA.NS","LATENTVIEW.NS","RATEGAIN.NS","ROUTE.NS",
                                        "TANLA.NS","HAPPSTMNDS.NS"],
    "Smallcap — Pharma"             : ["IPCALAB.NS","AJANTPHARM.NS","JBCHEPHARM.NS",
                                        "SUVENPHAR.NS","GLAND.NS","ERIS.NS","NEULANDLAB.NS"],
    "Smallcap — Chemicals"          : ["ROSSARI.NS","ANURAS.NS","CLEAN.NS","NEOGEN.NS",
                                        "AMIORG.NS","NOCIL.NS"],
    "Smallcap — Textiles"           : ["KPRMILL.NS","TRIDENT.NS","ICIL.NS","GOKALDAS.NS",
                                        "WELSPUNIND.NS"],
    "Smallcap — Infra & Construction": ["PSPPROJECT.NS","AHLUCONT.NS","HGINFRA.NS",
                                         "ASHOKA.NS","NCC.NS"],
    # ── All Midcap / All Smallcap ──────────────────────────────────────────────
    "⭐ All Midcap stocks"           : list(dict.fromkeys([
                                        "SHRIRAMFIN.NS","CHOLAFIN.NS","MUTHOOTFIN.NS","AUBANK.NS",
                                        "IDFCFIRSTB.NS","FEDERALBNK.NS","BANKBARODA.NS","PNB.NS",
                                        "CANBK.NS","IIFL.NS","CANFINHOME.NS","HOMEFIRST.NS",
                                        "FIVESTAR.NS","ANGELONE.NS","MOTILALOFS.NS","HDFCAMC.NS",
                                        "NAM-INDIA.NS","CAMS.NS","CDSL.NS","BSE.NS","MCX.NS",
                                        "360ONE.NS","ABCAPITAL.NS","STARHEALTH.NS",
                                        "PERSISTENT.NS","MPHASIS.NS","COFORGE.NS","LTIM.NS",
                                        "TATAELXSI.NS","KPITTECH.NS","HAPPSTMNDS.NS","BIRLASOFT.NS",
                                        "CYIENT.NS","ZENSARTECH.NS","MASTEK.NS","ROUTE.NS",
                                        "TANLA.NS","RATEGAIN.NS","LATENTVIEW.NS",
                                        "BALKRISIND.NS","MRF.NS","CEAT.NS","APOLLOTYRE.NS",
                                        "UNOMINDA.NS","ENDURANCE.NS","SANSERA.NS","TIINDIA.NS",
                                        "SUPRAJIT.NS","CRAFTSMAN.NS","RKFORGE.NS",
                                        "SRF.NS","NAVINFLUOR.NS","FLUOROCHEM.NS","DEEPAKNTR.NS",
                                        "AARTIIND.NS","FINEORG.NS","VINATIORGA.NS","ATUL.NS",
                                        "ALKYLAMINE.NS","LXCHEM.NS","GALAXYSURF.NS","BALAMINES.NS",
                                        "DEEPAKFERT.NS","TATACHEM.NS",
                                        "DLF.NS","GODREJPROP.NS","OBEROIRLTY.NS","PRESTIGE.NS",
                                        "BRIGADE.NS","PHOENIXLTD.NS","KEC.NS","KPIL.NS",
                                        "NCC.NS","PNCINFRA.NS","GRINFRA.NS","HGINFRA.NS",
                                        "ASHOKA.NS","RITES.NS","RAILTEL.NS","IRCON.NS","NBCC.NS",
                                        "POLYCAB.NS","KEI.NS","RRKABEL.NS","FINCABLES.NS",
                                        "APLAPOLLO.NS","RATNAMANI.NS","HAVELLS.NS","CROMPTON.NS",
                                        "VOLTAS.NS",
                                        "INDHOTEL.NS","LEMONTREE.NS","CHALET.NS",
                                        "ZOMATO.NS","PAYTM.NS","NYKAA.NS","DELHIVERY.NS","POLICYBZR.NS",
                                    ])),
    "⭐ All Smallcap stocks"         : list(dict.fromkeys([
                                        "BEL.NS","HAL.NS","BDL.NS","DATAPATTNS.NS","MTARTECH.NS",
                                        "PARAS.NS","IDEAFORGE.NS","GRSE.NS","MAZDOCK.NS",
                                        "COCHINSHIP.NS","BEML.NS","SOLARINDS.NS","ASTRAMICRO.NS",
                                        "MIDHANI.NS",
                                        "SYRMA.NS","KAYNES.NS","DIXON.NS","AMBER.NS","AVALON.NS",
                                        "ELIN.NS","HFCL.NS",
                                        "NAZARA.NS","LATENTVIEW.NS","RATEGAIN.NS","ROUTE.NS",
                                        "TANLA.NS",
                                        "IPCALAB.NS","AJANTPHARM.NS","JBCHEPHARM.NS","SUVENPHAR.NS",
                                        "GLAND.NS","ERIS.NS","NEULANDLAB.NS",
                                        "ROSSARI.NS","ANURAS.NS","CLEAN.NS","NEOGEN.NS",
                                        "AMIORG.NS","NOCIL.NS",
                                        "KPRMILL.NS","TRIDENT.NS","ICIL.NS","GOKALDAS.NS",
                                        "WELSPUNIND.NS",
                                        "PSPPROJECT.NS","AHLUCONT.NS",
                                        "AVANTIFEED.NS","ZYDUSWELL.NS","BECTORFOOD.NS",
                                        "DODLA.NS","PARAGMILK.NS",
                                    ])),
    # ── Sector scans ───────────────────────────────────────────────────────────
    "IT & Tech (all caps)"          : ["TCS.NS","INFY.NS","WIPRO.NS","HCLTECH.NS","TECHM.NS",
                                        "PERSISTENT.NS","MPHASIS.NS","COFORGE.NS","LTIM.NS",
                                        "TATAELXSI.NS","KPITTECH.NS","HAPPSTMNDS.NS",
                                        "CYIENT.NS","ROUTE.NS","TANLA.NS","RATEGAIN.NS",
                                        "LATENTVIEW.NS","NAZARA.NS","HFCL.NS","ZENSARTECH.NS"],
    "Banking & Finance (all caps)"  : ["HDFCBANK.NS","ICICIBANK.NS","AXISBANK.NS","SBIN.NS",
                                        "KOTAKBANK.NS","BAJFINANCE.NS","INDUSINDBK.NS",
                                        "AUBANK.NS","IDFCFIRSTB.NS","FEDERALBNK.NS",
                                        "BANKBARODA.NS","PNB.NS","CANBK.NS","SHRIRAMFIN.NS",
                                        "CHOLAFIN.NS","MUTHOOTFIN.NS","ANGELONE.NS","CDSL.NS"],
}

# "All stocks in list" = union of every other group (deduped, indices excluded)
SCAN_GROUPS["All stocks in list"] = list(dict.fromkeys(
    t for grp in SCAN_GROUPS.values() for t in grp
    if t and not t.startswith("^")
))

# Reorder so the most-used groups appear first in the dropdown
_ORDER = [
    "All stocks in list",
    "⭐ All Midcap stocks",
    "⭐ All Smallcap stocks",
    "Nifty 50",
    "IT & Tech (all caps)",
    "Banking & Finance (all caps)",
]
SCAN_GROUPS = {k: SCAN_GROUPS[k] for k in _ORDER if k in SCAN_GROUPS}

# ── Auto-scan every hour (always on, Short Term logic) ────────────────────────
AUTO_SCAN_TICKERS = SCAN_GROUPS["All stocks in list"]

@st.cache_resource
def _get_bg_state():
    """Shared dict that persists across reruns — used for background thread communication."""
    return {"running": False, "done": False, "alerts": [], "ts": 0.0, "style": ""}

_bg = _get_bg_state()

# Always active — trigger page rerun every 1 hour
st_autorefresh(interval=3_600_000, key="auto_refresh_timer")

now       = time.time()
last_scan = st.session_state.get("auto_last_scan", 0)
one_hour  = 60 * 60

# Pick up results if background thread finished
if _bg["done"] and _bg["ts"] > last_scan:
    st.session_state["auto_buy_alerts"] = _bg["alerts"]
    st.session_state["auto_last_scan"]  = _bg["ts"]
    st.session_state["auto_scan_style"] = _bg["style"]
    _bg["done"] = False

# Start background thread if scan is due and not already running
if now - last_scan >= one_hour and not _bg["running"]:
    _bg["running"] = True
    # Fixed to Short Term (1–8 weeks): interval=1d, period=1y, vol_mult=1.1
    _iv, _per, _vm, _st = "1d", "1y", 1.1, "Short Term (1–8 weeks)"

    def _do_scan(_iv=_iv, _per=_per, _vm=_vm, _st=_st):
        alerts = []
        for tkr in AUTO_SCAN_TICKERS:
            try:
                sdf = fetch_and_process(tkr, _iv, _per, _vm)
                if sdf is None or len(sdf) < 30:
                    continue
                sig, price_, *_ = get_live_signal(sdf, _iv)
                if "BUY" in sig:
                    name = next((n for n, t in NSE_STOCKS.items() if t == tkr), tkr)
                    alerts.append({"name": name, "ticker": tkr, "price": round(price_, 2)})
            except Exception:
                continue
        _bg["alerts"]  = alerts
        _bg["ts"]      = time.time()
        _bg["style"]   = _st
        _bg["done"]    = True
        _bg["running"] = False

    threading.Thread(target=_do_scan, daemon=True).start()
    st.session_state["auto_scan_style"] = "Short Term (1–8 weeks)"

if _bg["running"]:
    st.sidebar.caption("🔄 Scanning in background…")

# ── Floating ALERT panel (top-right, always visible) ──────────────────────────
buy_alerts  = st.session_state.get("auto_buy_alerts", [])
last_scan_t = st.session_state.get("auto_last_scan", 0)

if buy_alerts:
    def _alert_row(a):
        sym = a['ticker'].replace(".NS", "").replace(".BO", "")
        url = f"https://www.tradingview.com/chart/?symbol=NSE:{sym}"
        return (
            f"<div style='display:flex;justify-content:space-between;align-items:center;"
            f"padding:3px 0;border-bottom:1px solid #1e3a1e;font-size:11px;gap:6px'>"
            f"<a href='{url}' target='_blank' style='color:#86efac;font-weight:600;"
            f"text-decoration:none;white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>{a['name'][:16]}</a>"
            f"<span style='color:#4ade80;font-size:10px;white-space:nowrap'>₹{a['price']:,.2f}</span></div>"
        )

    # Split into two columns
    mid = (len(buy_alerts) + 1) // 2
    col1_html = "".join(_alert_row(a) for a in buy_alerts[:mid])
    col2_html = "".join(_alert_row(a) for a in buy_alerts[mid:])
    rows_html = (
        f"<div style='display:grid;grid-template-columns:1fr 1fr;gap:0 6px;"
        f"border-top:1px solid #1e3a1e;margin-top:4px;padding-top:4px'>"
        f"<div>{col1_html}</div><div>{col2_html}</div></div>"
    )
    scanned_at = time.strftime("%H:%M", time.localtime(last_scan_t)) if last_scan_t else "—"
    panel_html = f"""
    <div style="position:fixed;top:60px;right:12px;z-index:9999;
                background:#052e16;border:1px solid #166534;border-radius:10px;
                padding:12px 14px;min-width:320px;max-width:380px;
                box-shadow:0 4px 20px rgba(0,0,0,0.5);">
      <div style="font-size:11px;color:#86efac;letter-spacing:1px;
                  font-weight:700;margin-bottom:2px;">
        🟢 ALERT &nbsp;·&nbsp; {len(buy_alerts)} BUY signals
      </div>
      <div style="font-size:10px;color:#4ade80;opacity:0.75;margin-bottom:4px;">
        Short Term · 1d
      </div>
      {rows_html}
      <div style="font-size:10px;color:#4ade80;margin-top:7px;opacity:0.7">
        Last scanned: {scanned_at} &nbsp;·&nbsp; Next: +1h
      </div>
    </div>
    """
else:
    scanned_at = time.strftime("%H:%M", time.localtime(last_scan_t)) if last_scan_t else "scanning…"
    panel_html = f"""
    <div style="position:fixed;top:60px;right:12px;z-index:9999;
                background:#0f172a;border:1px solid #1e293b;border-radius:10px;
                padding:12px 14px;min-width:200px;
                box-shadow:0 4px 20px rgba(0,0,0,0.5);">
      <div style="font-size:11px;color:#94a3b8;letter-spacing:1px;font-weight:600">
        🔔 ALERT &nbsp;·&nbsp; Short Term · 1d
      </div>
      <div style="font-size:11px;color:#64748b;margin-top:5px">
        No BUY signals right now<br>Last: {scanned_at} · Next: +1h
      </div>
    </div>
    """
st.markdown(panel_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Chart & Backtest
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊  Chart & Backtest":
    if df is None:
        st.info("Configure settings in the sidebar and click **Run Backtest**.")
        st.stop()

    # ── LIVE SIGNAL PANEL ─────────────────────────────────────────────────────
    signal, price, rsi_val, ema9, ema21, vol, avg_vol, conditions = get_live_signal(df, interval)
    adx_val  = float(df.iloc[-1]["adx"])  if not np.isnan(df.iloc[-1]["adx"])  else 0
    vwap_val = float(df.iloc[-1]["vwap"]) if not np.isnan(df.iloc[-1]["vwap"]) else 0
    ema50_val= float(df.iloc[-1]["ema50"])

    if "BUY" in signal:
        bg, icon, txt = "#052e16", "🟢", signal
    elif "SELL" in signal:
        bg, icon, txt = "#2d0a0a", "🔴", signal
    elif "Watch" in signal:
        bg, icon, txt = "#1c1a06", "👀", signal
    else:
        bg, icon, txt = "#0f172a", "⏸", signal

    st.markdown(f"""
    <div style="background:{bg};border-radius:10px;padding:10px 20px;margin-bottom:8px;
                border:1px solid #334155;">
      <div style="font-size:11px;color:#94a3b8;margin-bottom:2px;">
        CURRENT SIGNAL — {cur_tick} ({cur_int})
      </div>
      <div style="font-size:26px;font-weight:800;letter-spacing:1px;">
        {icon} {txt}
      </div>
      <div style="margin-top:4px;font-size:13px;color:#cbd5e1;">
        Price: <b>₹{price:,.2f}</b> &nbsp;|&nbsp;
        RSI: <b>{rsi_val:.1f}</b> &nbsp;|&nbsp;
        ADX: <b>{adx_val:.1f}</b> &nbsp;|&nbsp;
        EMA9: <b>{ema9:,.2f}</b> &nbsp;|&nbsp;
        EMA21: <b>{ema21:,.2f}</b> &nbsp;|&nbsp;
        EMA50: <b>{ema50_val:,.2f}</b>{"" if cur_int in ("1d","1wk","1mo") else f" &nbsp;|&nbsp; VWAP: <b>₹{vwap_val:,.2f}</b>"} &nbsp;|&nbsp;
        Volume: <b>{vol:,.0f}</b> (avg {avg_vol:,.0f})
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Why this signal? — Condition Checklist"):
        if cur_int == "1mo":
            buy_conditions = [
                "EMA crossover within last 3 months",
                "EMA9 > EMA21 (short-term uptrend)",
                "Price above EMA50 (macro uptrend)",
                "RSI rising (momentum)",
                "RSI in buy zone",
            ]
            sell_conditions = [
                "EMA crossover within last 3 months",
                "EMA9 < EMA21 (short-term downtrend)",
                "Price above EMA50 (macro uptrend)",
                "RSI rising (momentum)",
                "RSI in buy zone",
            ]
        elif cur_int == "1wk":
            buy_conditions = [
                "EMA crossover within last 4 weeks",
                "EMA9 > EMA21 (short-term uptrend)",
                "Price above EMA50 (macro uptrend)",
                "RSI rising (momentum)",
                "RSI in buy zone",
                "Volume confirmed",
            ]
            sell_conditions = [
                "EMA crossover within last 4 weeks",
                "EMA9 < EMA21 (short-term downtrend)",
                "Price above EMA50 (macro uptrend)",
                "RSI rising (momentum)",
                "RSI in buy zone",
                "Volume confirmed",
            ]
        elif cur_int == "1d":
            buy_conditions = [
                "EMA crossover within last 5 days",
                "EMA9 > EMA21 (short-term uptrend)",
                "Price above EMA50 (macro uptrend)",
                "RSI rising (momentum)",
                "RSI in buy zone",
                "Volume confirmed",
            ]
            sell_conditions = [
                "EMA crossover within last 5 days",
                "EMA9 < EMA21 (short-term downtrend)",
                "Price above EMA50 (macro uptrend)",
                "RSI rising (momentum)",
                "RSI in buy zone",
                "Volume confirmed",
            ]
        else:
            buy_conditions = [
                "EMA crossover just fired",
                "EMA9 > EMA21 (short-term uptrend)",
                "Price above EMA50 (macro uptrend)",
                "Price above VWAP (insti. buying)",
                "RSI in buy zone",
                "Volume confirmed",
                "ADX > 20 (trending market)",
            ]
            sell_conditions = [
                "EMA crossover just fired",
                "EMA9 < EMA21 (short-term downtrend)",
                "Price above EMA50 (macro uptrend)",
                "Price above VWAP (insti. buying)",
                "RSI in buy zone",
                "Volume confirmed",
                "ADX > 20 (trending market)",
            ]

        col_b, col_s = st.columns(2)
        with col_b:
            st.markdown("**BUY conditions**")
            for c in buy_conditions:
                st.markdown(f"{'✅' if conditions.get(c) else '❌'} {c}")
        with col_s:
            st.markdown("**SELL conditions**")
            for c in sell_conditions:
                st.markdown(f"{'✅' if conditions.get(c) else '❌'} {c}")
        n = 5 if cur_int == "1mo" else (6 if cur_int in ("1wk","1d") else 7)
        st.caption(f"All {n} must be ✅ for a confirmed BUY/SELL signal.")

    # ── Summary cards ─────────────────────────────────────────────────────────
    st.markdown("<p style='font-size:1rem;font-weight:600;margin:6px 0 2px'>Backtest Summary</p>", unsafe_allow_html=True)
    if trades_df.empty:
        st.warning("No trades found. Try a different ticker, interval, or loosen the volume filter.")
    else:
        wins      = trades_df[trades_df["pnl_%"] > 0]
        losses    = trades_df[trades_df["pnl_%"] <= 0]
        total_pnl = trades_df["pnl_%"].sum()
        win_rate  = len(wins) / len(trades_df) * 100
        avg_win   = wins["pnl_%"].mean()   if len(wins)   else 0

        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Total Trades", len(trades_df))
        c2.metric("Wins",  len(wins))
        c3.metric("Losses", len(losses))
        c4.metric("Win Rate", f"{win_rate:.1f}%")
        c5.metric("Avg Win",  f"{avg_win:+.2f}%")
        c6.metric("Total P&L", f"{total_pnl:+.2f}%",
                  delta_color="normal" if total_pnl >= 0 else "inverse")

    # ── Chart ─────────────────────────────────────────────────────────────────
    st.plotly_chart(
        build_chart(df, trades_df, cur_tick, cur_int, stop_pct, target_pct),
        use_container_width=True,
    )

    # ── Trade table ───────────────────────────────────────────────────────────
    if not trades_df.empty:
        st.subheader("All Trades")
        display = trades_df.copy()
        display["entry_time"] = display["entry_time"].astype(str).str[:16]
        display["exit_time"]  = display["exit_time"].astype(str).str[:16]
        display.index = range(1, len(display) + 1)

        def color_pnl(val):
            color = "#22c55e" if val > 0 else "#ef5350"
            return f"color: {color}; font-weight: bold"

        def color_side(val):
            color = "#26a69a" if val == "LONG" else "#ef5350"
            return f"color: {color}; font-weight: bold"

        st.dataframe(
            display.style
                .apply(lambda col: col.map(color_pnl),  axis=0, subset=["pnl_%"])
                .apply(lambda col: col.map(color_side), axis=0, subset=["side"]),
            use_container_width=True,
            height=min(400, 38 + len(display) * 35),
        )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — Stock Scanner
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍  Stock Scanner":
    st.markdown("<p style='font-size:1.1rem;font-weight:600;margin-bottom:2px'>🔍 Scan NSE Stocks for BUY / SELL Signals</p>", unsafe_allow_html=True)
    st.caption("Checks every stock in the list against the current strategy settings.")

    # Let user choose which group to scan
    col_g, col_b, col_s = st.columns([3, 1, 1])
    with col_g:
        group = st.selectbox("Stock group to scan", list(SCAN_GROUPS.keys()), index=0)
    with col_b:
        st.write("")
        st.write("")
        buy_btn = st.button("🟢 BUY Signals", type="primary", use_container_width=True)
    with col_s:
        st.write("")
        st.write("")
        sell_btn = st.button("🔴 SELL Signals", use_container_width=True)

    scan_mode = "BUY" if buy_btn else ("SELL" if sell_btn else None)

    if scan_mode:
        st.session_state["scan_mode"]  = scan_mode
        st.session_state["scan_group"] = group
        tickers_to_scan = [t for t in SCAN_GROUPS[group] if t and not t.startswith("^")]
        results = []
        label   = scan_mode
        prog    = st.progress(0, text=f"Scanning for {label} signals…")

        for i, tkr in enumerate(tickers_to_scan):
            prog.progress((i + 1) / len(tickers_to_scan), text=f"Checking {tkr}…")
            try:
                sdf = fetch_and_process(tkr, interval, period, vol_mult)
                if sdf is None or len(sdf) < 30:
                    continue
                sig, price_, rsi_, ema9_, ema21_, vol_, avg_vol_, conds = get_live_signal(sdf, interval)
                name = next((n for n, t in NSE_STOCKS.items() if t == tkr), tkr)

                # Approx target: recent swing high (60 bars) or at least 8% above entry (BUY)
                #                recent swing low  (60 bars) or at least 8% below entry (SELL)
                try:
                    highs = list(sdf["high"].dropna().astype(float))
                    lows  = list(sdf["low"].dropna().astype(float))
                    n60h  = highs[-min(60, len(highs)):]
                    n60l  = lows[-min(60, len(lows)):]
                    if "BUY" in sig or "Bullish" in sig:
                        tgt    = round(max(max(n60h), price_ * 1.08), 2)
                    elif "SELL" in sig or "Bearish" in sig:
                        tgt    = round(min(min(n60l), price_ * 0.92), 2)
                    else:
                        tgt = None
                    upside = round((tgt - price_) / price_ * 100, 1) if tgt else None
                except Exception:
                    tgt, upside = None, None

                results.append({
                    "Signal"    : sig,
                    "Company"   : name,
                    "Ticker"    : tkr,
                    "Price ₹"   : round(price_, 2),
                    "Target ₹"  : tgt,
                    "Upside %"  : upside,
                    "RSI"       : round(rsi_, 1),
                    "EMA9"      : round(ema9_, 2),
                    "EMA21"     : round(ema21_, 2),
                    "Vol / Avg" : f"{vol_/avg_vol_:.2f}x" if avg_vol_ else "—",
                })
            except Exception:
                continue

        prog.empty()
        st.session_state["scan_results"]   = results
        st.session_state["scan_style"]     = style
        st.session_state["scan_interval"]  = interval

    # ── Clear stale results if trading style / interval changed ─────────────
    if (st.session_state.get("scan_interval") and
            st.session_state.get("scan_interval") != interval):
        for k in ("scan_results", "scan_mode", "scan_group", "scan_style", "scan_interval"):
            st.session_state.pop(k, None)

    # ── Display scan results (from session state so they survive reruns) ───────
    results    = st.session_state.get("scan_results")
    scan_mode  = st.session_state.get("scan_mode")
    scan_group = st.session_state.get("scan_group", group)
    scan_style_used = st.session_state.get("scan_style", style)

    def highlight_signal(val):
        v = str(val)
        if "BUY"     in v: return "color:#16a34a;font-weight:600"
        if "SELL"    in v: return "color:#dc2626;font-weight:600"
        if "Bullish" in v: return "color:#16a34a;font-weight:500"
        if "Bearish" in v: return "color:#ea580c;font-weight:500"
        return "color:#94a3b8"

    def highlight_rsi_row(row):
        styles = [""] * len(row)
        try:
            rsi_num = float(row["RSI"])
            sig     = str(row["Signal"])
            rsi_idx = row.index.get_loc("RSI")
            if ("BUY" in sig and rsi_num >= 68) or ("SELL" in sig and rsi_num <= 32):
                styles[rsi_idx] = "background-color:#fee2e2;color:#dc2626;font-weight:700"
        except (ValueError, TypeError, KeyError):
            pass
        return styles

    def render_table(rows, key_prefix):
        """Render scan results with clickable company name linking to TradingView."""
        df_display = pd.DataFrame([{
            "Signal"   : r["Signal"],
            "Company"  : f"https://www.tradingview.com/chart/?symbol=NSE:{r['Ticker'].replace('.NS','').replace('.BO','')}",
            "Ticker"   : r["Ticker"],
            "Price ₹"  : f"₹{r['Price ₹']:,.2f}",
            "Target ₹" : f"₹{r['Target ₹']:,.2f}" if r.get("Target ₹") else "—",
            "Upside %"  : r.get("Upside %"),
            "RSI"      : r["RSI"],
            "EMA9"     : f"{r['EMA9']:,.2f}",
            "EMA21"    : f"{r['EMA21']:,.2f}",
            "Vol/Avg"  : r["Vol / Avg"],
        } for r in rows])

        def color_upside(val):
            try:
                v = float(val)
                return "color:#16a34a;font-weight:600" if v > 0 else "color:#dc2626;font-weight:600"
            except Exception:
                return ""

        st.dataframe(
            df_display.style
                .apply(lambda col: col.map(highlight_signal), axis=0, subset=["Signal"])
                .apply(highlight_rsi_row, axis=1)
                .map(color_upside, subset=["Upside %"]),
            use_container_width=True,
            height=min(500, 38 + len(rows) * 35),
            hide_index=True,
            column_config={
                "Company": st.column_config.LinkColumn(
                    "Company",
                    display_text=r"symbol=NSE:([^&]+)",
                    help="Open on TradingView",
                ),
                "Upside %": st.column_config.NumberColumn(
                    "Upside %",
                    format="%.1f%%",
                    help="(Target − Price) / Price. BUY: upside to swing high; SELL: downside to swing low.",
                ),
            }
        )

    if results is None:
        st.info("Select a stock group, then click **🟢 BUY Signals** or **🔴 SELL Signals** to scan.")
    else:
        rdf     = pd.DataFrame(results)
        label   = scan_mode
        matches = rdf[rdf["Signal"].str.contains(scan_mode, na=False)].copy()
        watches = rdf[rdf["Signal"].str.contains("Watch", na=False)].copy()

        s1, s2, s3 = st.columns(3)
        icon = "🟢" if scan_mode == "BUY" else "🔴"
        s1.metric(f"{icon} {label} signals found", len(matches))
        s2.metric("🟡 Almost ready (WATCH)", len(watches))
        s3.metric("Total scanned", len(rdf))
        st.caption(f"Trading Style: **{scan_style_used}** · {interval} · {period}")

        if matches.empty:
            st.warning(f"No {label} signals right now. Check the WATCH list below — those are close.")
        else:
            header = "### 🟢 BUY Signals — Stocks to Enter" if scan_mode == "BUY" else "### 🔴 SELL / SHORT Signals"
            st.markdown(header)
            render_table(matches.to_dict("records"), key_prefix="match")

        if not watches.empty:
            with st.expander(f"👀 {len(watches)} stocks almost ready — WATCH list (1 condition missing)"):
                render_table(watches.to_dict("records"), key_prefix="watch")

        _sl_str = f"{atr_sl_mult}×ATR" if use_atr else f"{stop_pct*100:.1f}%"
        _tp_str = f"{atr_tp_mult}×ATR" if use_atr else f"{target_pct*100:.1f}%"
        st.caption(f"Scanned {len(rdf)} stocks · {interval} · {period} · "
                   f"Vol ≥{vol_mult}x · SL {_sl_str} · TP {_tp_str}")
