#!/usr/bin/env python3
"""
NSE F&O Screener — Daily Excel Export
Runs all 3 screeners and saves top-20 results to a dated .xlsx file.

Schedule via cron (3 PM IST, weekdays):
    crontab -e
    0 15 * * 1-5 cd /Users/I325211/Local_Project/Analysis && python3 daily_export.py >> exports/export_log.txt 2>&1
"""

import os, io, re, datetime, json
import pandas as pd
import yfinance as yf
import requests

# ── Paths ─────────────────────────────────────────────────────────────────────
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
EXPORTS_DIR = os.path.join(SCRIPT_DIR, "exports")
os.makedirs(EXPORTS_DIR, exist_ok=True)

TODAY     = datetime.date.today().strftime("%Y-%m-%d")
NOW       = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
OUTFILE   = os.path.join(EXPORTS_DIR, f"screener_{TODAY}.xlsx")
HIST_FILE = os.path.join(EXPORTS_DIR, "consolidated_history.xlsx")

def log(msg):
    print(f"[{datetime.datetime.now():%H:%M:%S}] {msg}", flush=True)

# ── Company names ─────────────────────────────────────────────────────────────
COMPANY_NAMES = {
    "ABB":"ABB India","POWERINDIA":"Hitachi Energy India","ADANIENT":"Adani Enterprises",
    "ADANIGREEN":"Adani Green Energy","ADANIPORTS":"Adani Ports & SEZ","ADANIPOWER":"Adani Power",
    "ADANIENSOL":"Adani Energy Solutions","ABCAPITAL":"Aditya Birla Capital","ALKEM":"Alkem Laboratories",
    "GVT&D":"GE Vernova T&D India","AMBUJACEM":"Ambuja Cements","AMBER":"Amber Enterprises India",
    "ANGELONE":"Angel One","APLAPOLLO":"APL Apollo Tubes","APOLLOHOSP":"Apollo Hospitals",
    "ASHOKLEY":"Ashok Leyland","ASIANPAINT":"Asian Paints","ASTRAL":"Astral",
    "AUROPHARMA":"Aurobindo Pharma","AUBANK":"AU Small Finance Bank","DMART":"Avenue Supermarts",
    "AXISBANK":"Axis Bank","BAJAJ-AUTO":"Bajaj Auto","BAJAJFINSV":"Bajaj Finserv",
    "BAJFINANCE":"Bajaj Finance","BAJAJHLDNG":"Bajaj Holdings","BANDHANBNK":"Bandhan Bank",
    "BANKBARODA":"Bank of Baroda","BANKINDIA":"Bank of India","BHARTIARTL":"Bharti Airtel",
    "BDL":"Bharat Dynamics","BEL":"Bharat Electronics","BHARATFORG":"Bharat Forge",
    "INDUSTOWER":"Indus Towers","BPCL":"BPCL","BHEL":"BHEL","BIOCON":"Biocon",
    "BLUESTARCO":"Blue Star","BOSCHLTD":"Bosch India","BRITANNIA":"Britannia Industries",
    "BSE":"BSE","ZYDUSLIFE":"Zydus Lifesciences","CANBK":"Canara Bank","CDSL":"CDSL",
    "CHOLAFIN":"Cholamandalam Investment","CIPLA":"Cipla","COALINDIA":"Coal India",
    "COCHINSHIP":"Cochin Shipyard","COLPAL":"Colgate-Palmolive India","CAMS":"CAMS",
    "CONCOR":"Container Corp","CROMPTON":"Crompton Greaves Consumer","CGPOWER":"CG Power",
    "CUMMINSIND":"Cummins India","DABUR":"Dabur India","DELHIVERY":"Delhivery",
    "DIVISLAB":"Divi's Laboratories","DIXON":"Dixon Technologies","DLF":"DLF",
    "DRREDDY":"Dr. Reddy's Laboratories","EICHERMOT":"Eicher Motors","FEDERALBNK":"Federal Bank",
    "FORTIS":"Fortis Healthcare","FORCEMOT":"Force Motors","NYKAA":"Nykaa",
    "GAIL":"GAIL India","GLENMARK":"Glenmark Pharmaceuticals","GMRAIRPORT":"GMR Airports",
    "GODREJCP":"Godrej Consumer Products","GODFRYPHLP":"Godfrey Phillips India",
    "GODREJPROP":"Godrej Properties","GRASIM":"Grasim Industries","HAVELLS":"Havells India",
    "HCLTECH":"HCL Technologies","HDFCAMC":"HDFC AMC","HDFCBANK":"HDFC Bank",
    "HDFCLIFE":"HDFC Life Insurance","HEROMOTOCO":"Hero MotoCorp","HAL":"HAL",
    "HINDALCO":"Hindalco Industries","HINDUNILVR":"Hindustan Unilever","HINDPETRO":"HPCL",
    "HINDZINC":"Hindustan Zinc","HYUNDAI":"Hyundai Motor India","ICICIBANK":"ICICI Bank",
    "ICICIGI":"ICICI Lombard GI","ICICIPRULI":"ICICI Prudential Life","IDEA":"Vodafone Idea",
    "IDFCFIRSTB":"IDFC First Bank","360ONE":"360 ONE WAM","INDUSINDBK":"IndusInd Bank",
    "IEX":"Indian Energy Exchange","INDHOTEL":"Indian Hotels (Taj)","INDIANB":"Indian Bank",
    "IOC":"Indian Oil Corp","IRFC":"IRFC","IREDA":"IREDA","NAUKRI":"Info Edge (Naukri)",
    "INFY":"Infosys","INOXWIND":"INOX Wind","INDIGO":"IndiGo","ITC":"ITC",
    "JINDALSTEL":"Jindal Steel & Power","JIOFIN":"Jio Financial Services","JSWENERGY":"JSW Energy",
    "JSWSTEEL":"JSW Steel","JUBLFOOD":"Jubilant FoodWorks","KALYANKJIL":"Kalyan Jewellers",
    "KAYNES":"Kaynes Technology","KEI":"KEI Industries","KFINTECH":"KFin Technologies",
    "KOTAKBANK":"Kotak Mahindra Bank","KPITTECH":"KPIT Technologies","LT":"Larsen & Toubro",
    "LAURUSLABS":"Laurus Labs","LICI":"LIC India","LICHSGFIN":"LIC Housing Finance",
    "LTF":"L&T Finance","LTM":"LTIMindtree","LUPIN":"Lupin","LODHA":"Lodha Developers",
    "M&M":"Mahindra & Mahindra","MANAPPURAM":"Manappuram Finance","MANKIND":"Mankind Pharma",
    "MARICO":"Marico","MARUTI":"Maruti Suzuki","MFSL":"Max Financial Services",
    "MAXHEALTH":"Max Healthcare","MAZDOCK":"Mazagon Dock","MCX":"MCX",
    "UNOMINDA":"UNO Minda","MOTILALOFS":"Motilal Oswal","MOTHERSON":"Motherson Sumi",
    "MPHASIS":"Mphasis","MUTHOOTFIN":"Muthoot Finance","NATIONALUM":"National Aluminium",
    "NMDC":"NMDC","NBCC":"NBCC India","NESTLEIND":"Nestle India","NHPC":"NHPC",
    "COFORGE":"Coforge","NTPC":"NTPC","OBEROIRLTY":"Oberoi Realty","DALBHARAT":"Dalmia Bharat",
    "OIL":"Oil India","PAYTM":"Paytm","ONGC":"ONGC","OFSS":"Oracle Financial Services",
    "PAGEIND":"Page Industries","POLICYBZR":"PB Fintech","PERSISTENT":"Persistent Systems",
    "PETRONET":"Petronet LNG","PGEL":"PG Electroplast","PHOENIXLTD":"Phoenix Mills",
    "PIDILITIND":"Pidilite Industries","PIIND":"PI Industries","PNBHOUSING":"PNB Housing Finance",
    "POLYCAB":"Polycab India","PFC":"Power Finance Corp","POWERGRID":"Power Grid Corp",
    "PREMIERENE":"Premier Energies","PRESTIGE":"Prestige Estates","PNB":"Punjab National Bank",
    "RADICO":"Radico Khaitan","RVNL":"RVNL","RBLBANK":"RBL Bank","RELIANCE":"Reliance Industries",
    "NAM-INDIA":"Nippon India AMC","PATANJALI":"Patanjali Foods","RECLTD":"REC",
    "SAIL":"SAIL","SBICARD":"SBI Cards","SBILIFE":"SBI Life Insurance","SHREECEM":"Shree Cement",
    "SHRIRAMFIN":"Shriram Finance","SIEMENS":"Siemens India","SOLARINDS":"Solar Industries",
    "SONACOMS":"Sona BLW","SRF":"SRF","SBIN":"State Bank of India","SUNPHARMA":"Sun Pharma",
    "SUPREMEIND":"Supreme Industries","SUZLON":"Suzlon Energy","SWIGGY":"Swiggy",
    "TATAELXSI":"Tata Elxsi","TATACONSUM":"Tata Consumer Products","TATAMOTORS":"Tata Motors",
    "TATAPOWER":"Tata Power","TATASTEEL":"Tata Steel","TCS":"TCS","TECHM":"Tech Mahindra",
    "TITAN":"Titan Company","TORNTPHARM":"Torrent Pharmaceuticals","TRENT":"Trent",
    "TIINDIA":"Tube Investments","TVSMOTOR":"TVS Motor","ULTRACEMCO":"UltraTech Cement",
    "UNIONBANK":"Union Bank","UPL":"UPL","UNITDSPR":"United Spirits","VBL":"Varun Beverages",
    "VEDL":"Vedanta","VMM":"Vishal Mega Mart","VOLTAS":"Voltas","WAAREEENER":"Waaree Energies",
    "WIPRO":"Wipro","YESBANK":"Yes Bank","ETERNAL":"Eternal (Zomato)",
    "ATHERENERG":"Ather Energy","MAHABANK":"Bank of Maharashtra","SAGILITY":"Sagility India",
}

FNO_EXCLUDE = {
    "NIFTY","BANKNIFTY","FINNIFTY","MIDCPNIFTY","NIFTYNXT50",
    "NIFTYIT","UNDERLYING","SENSEX","BANKEX","NIFTY50","NIFTY100",
    "NIFTYFPI","TMPV",
}

CACHE_FILE = os.path.join(SCRIPT_DIR, "fno_cache.json")

def _load_fno_cache():
    try:
        with open(CACHE_FILE) as f:
            c = json.load(f)
        syms  = c.get("symbols", [])
        names = c.get("names", {})
        age   = (datetime.date.today() - datetime.date.fromisoformat(c.get("updated", "2000-01-01"))).days
        if len(syms) >= 50:
            return syms, names, age
    except Exception:
        pass
    return None, {}, None

def _save_fno_cache(symbols, names):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump({"updated": str(datetime.date.today()), "symbols": symbols, "names": names}, f)
    except Exception:
        pass

# ── Helpers ───────────────────────────────────────────────────────────────────
def fetch_fno_symbols():
    cached_syms, cached_names, cache_age = _load_fno_cache()
    if cached_syms is None or cache_age >= 7:
        try:
            r = requests.get("https://api.kite.trade/instruments", timeout=20)
            r.raise_for_status()
            df = pd.read_csv(io.StringIO(r.text))
            fno = df[(df["exchange"] == "NFO") & (df["instrument_type"] == "FUT")]
            syms = sorted({
                str(s).strip() for s in fno["name"].dropna().unique()
                if str(s).strip() not in FNO_EXCLUDE
            })
            if len(syms) >= 50:
                # Also fetch company names from NSE equity master
                names = dict(cached_names)
                try:
                    r2 = requests.get(
                        "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
                        timeout=20,
                    )
                    r2.raise_for_status()
                    eq = pd.read_csv(io.StringIO(r2.text))
                    sym_col  = eq.columns[0]
                    name_col = next((c for c in eq.columns if "NAME" in c.upper()), None)
                    if name_col:
                        for _, row in eq.iterrows():
                            s = str(row[sym_col]).strip()
                            n = str(row[name_col]).strip()
                            if s in syms and n and n.lower() != "nan":
                                names[s] = n.title()
                except Exception:
                    pass
                _save_fno_cache(syms, names)
                return syms, names, "Zerodha Live"
        except Exception:
            pass
        if cached_syms:
            return cached_syms, cached_names, f"Cache ({cache_age}d old)"
        return None, {}, "Bundled"
    return cached_syms, cached_names, "Cache (fresh)"

SECTOR = {
    "ABCAPITAL":"Financial Services","AXISBANK":"Financial Services","BAJAJFINSV":"Financial Services",
    "BAJFINANCE":"Financial Services","BAJAJHLDNG":"Financial Services","BANDHANBNK":"Financial Services",
    "BANKBARODA":"Financial Services","BANKINDIA":"Financial Services","BSE":"Financial Services",
    "CAMS":"Financial Services","CANBK":"Financial Services","CDSL":"Financial Services",
    "CHOLAFIN":"Financial Services","HDFCAMC":"Financial Services","HDFCBANK":"Financial Services",
    "HDFCLIFE":"Financial Services","ICICIBANK":"Financial Services","ICICIGI":"Financial Services",
    "ICICIPRULI":"Financial Services","IDFCFIRSTB":"Financial Services","IEX":"Financial Services",
    "INDUSINDBK":"Financial Services","INDIANB":"Financial Services","IRFC":"Financial Services",
    "JIOFIN":"Financial Services","KFINTECH":"Financial Services","KOTAKBANK":"Financial Services",
    "LICHSGFIN":"Financial Services","LICI":"Financial Services","LTF":"Financial Services",
    "MANAPPURAM":"Financial Services","MFSL":"Financial Services","MOTILALOFS":"Financial Services",
    "MUTHOOTFIN":"Financial Services","NAM-INDIA":"Financial Services","PFC":"Financial Services",
    "POLICYBZR":"Financial Services","PNB":"Financial Services","PNBHOUSING":"Financial Services",
    "RBLBANK":"Financial Services","RECLTD":"Financial Services","SBICARD":"Financial Services",
    "SBILIFE":"Financial Services","SHRIRAMFIN":"Financial Services","SBIN":"Financial Services",
    "UNIONBANK":"Financial Services","YESBANK":"Financial Services","360ONE":"Financial Services",
    "HCLTECH":"IT","INFY":"IT","KPITTECH":"IT","LTM":"IT","MPHASIS":"IT","OFSS":"IT",
    "PERSISTENT":"IT","TECHM":"IT","TCS":"IT","WIPRO":"IT","COFORGE":"IT","TATAELXSI":"IT",
    "ALKEM":"Pharma","AUROPHARMA":"Pharma","BIOCON":"Pharma","CIPLA":"Pharma","DIVISLAB":"Pharma",
    "DRREDDY":"Pharma","GLENMARK":"Pharma","LAURUSLABS":"Pharma","LUPIN":"Pharma",
    "MANKIND":"Pharma","SUNPHARMA":"Pharma","TORNTPHARM":"Pharma","ZYDUSLIFE":"Pharma",
    "ASHOKLEY":"Automobile","BAJAJ-AUTO":"Automobile","EICHERMOT":"Automobile","FORCEMOT":"Automobile",
    "HEROMOTOCO":"Automobile","M&M":"Automobile","MARUTI":"Automobile","TATAMOTORS":"Automobile",
    "TVSMOTOR":"Automobile","UNOMINDA":"Automobile","MOTHERSON":"Automobile",
    "ABB":"Capital Goods","BDL":"Capital Goods","BEL":"Capital Goods","BHARATFORG":"Capital Goods",
    "BLUESTARCO":"Capital Goods","BOSCHLTD":"Capital Goods","CGPOWER":"Capital Goods",
    "CUMMINSIND":"Capital Goods","DIXON":"Capital Goods","HAL":"Capital Goods","HAVELLS":"Capital Goods",
    "KEI":"Capital Goods","POLYCAB":"Capital Goods","SIEMENS":"Capital Goods","TIINDIA":"Capital Goods",
    "VOLTAS":"Capital Goods","KAYNES":"Capital Goods","PGEL":"Capital Goods","SONACOMS":"Capital Goods",
    "GVT&D":"Capital Goods","POWERINDIA":"Capital Goods","AMBER":"Capital Goods",
    "APLAPOLLO":"Capital Goods","SOLARINDS":"Capital Goods",
    "PIDILITIND":"Chemicals","PIIND":"Chemicals","SRF":"Chemicals","UPL":"Chemicals",
    "AMBUJACEM":"Cement","DALBHARAT":"Cement","SHREECEM":"Cement","ULTRACEMCO":"Cement","GRASIM":"Cement",
    "BRITANNIA":"Consumer Goods","COLPAL":"Consumer Goods","DABUR":"Consumer Goods","DMART":"Consumer Goods",
    "GODREJCP":"Consumer Goods","GODFRYPHLP":"Consumer Goods","ITC":"Consumer Goods",
    "JUBLFOOD":"Consumer Goods","MARICO":"Consumer Goods","NESTLEIND":"Consumer Goods",
    "PAGEIND":"Consumer Goods","PATANJALI":"Consumer Goods","RADICO":"Consumer Goods",
    "TITAN":"Consumer Goods","TATACONSUM":"Consumer Goods","UNITDSPR":"Consumer Goods",
    "VBL":"Consumer Goods","KALYANKJIL":"Consumer Goods","HINDUNILVR":"Consumer Goods",
    "CROMPTON":"Consumer Goods",
    "HINDALCO":"Metals & Mining","HINDZINC":"Metals & Mining","JSWSTEEL":"Metals & Mining",
    "JINDALSTEL":"Metals & Mining","NATIONALUM":"Metals & Mining","NMDC":"Metals & Mining",
    "SAIL":"Metals & Mining","TATASTEEL":"Metals & Mining","VEDL":"Metals & Mining",
    "BPCL":"Oil & Gas","GAIL":"Oil & Gas","HINDPETRO":"Oil & Gas","IOC":"Oil & Gas",
    "OIL":"Oil & Gas","ONGC":"Oil & Gas","PETRONET":"Oil & Gas",
    "DLF":"Real Estate","GODREJPROP":"Real Estate","LODHA":"Real Estate","OBEROIRLTY":"Real Estate",
    "PHOENIXLTD":"Real Estate","PRESTIGE":"Real Estate",
    "ADANIGREEN":"Power","ADANIPOWER":"Power","ADANIENSOL":"Power","JSWENERGY":"Power",
    "NHPC":"Power","NTPC":"Power","POWERGRID":"Power","SUZLON":"Power","TATAPOWER":"Power",
    "WAAREEENER":"Power","PREMIERENE":"Power","INOXWIND":"Power",
    "APOLLOHOSP":"Healthcare","FORTIS":"Healthcare","MAXHEALTH":"Healthcare",
    "ADANIENT":"Infrastructure","ADANIPORTS":"Infrastructure","GMRAIRPORT":"Infrastructure",
    "RVNL":"Infrastructure","NBCC":"Infrastructure","IREDA":"Infrastructure",
    "MAZDOCK":"Infrastructure","COCHINSHIP":"Infrastructure",
    "BHARTIARTL":"Telecom","IDEA":"Telecom","INDUSTOWER":"Telecom",
    "INDIGO":"Aviation","DELHIVERY":"Logistics","CONCOR":"Logistics",
    "ETERNAL":"E-Commerce","NYKAA":"E-Commerce","PAYTM":"Fintech","SWIGGY":"E-Commerce",
    "ATHERENERG":"Automobile","MAHABANK":"Financial Services","SAGILITY":"Healthcare",
}

def calc_ema(prices, n):
    k = 2 / (n + 1)
    e = prices[0]
    for p in prices[1:]:
        e = p * k + e * (1 - k)
    return e

# ── Screener 1: Probable Upside ───────────────────────────────────────────────
def run_probable_upside(fno, close_df, vol_df):
    rows = []
    for sym, nse, name in fno:
        try:
            ticker = f"{nse}.NS"
            cls_s  = close_df[ticker].dropna()
            vol_s  = vol_df[ticker].reindex(cls_s.index).fillna(0)
            cls    = list(cls_s.astype(float))
            vols   = list(vol_s.astype(float))
            if len(cls) < 20:
                continue
            cur       = cls[-1]
            sma20     = sum(cls[-20:]) / 20
            sma50     = sum(cls[-min(50, len(cls)):]) / min(50, len(cls))
            sma200    = sum(cls[-200:]) / 200 if len(cls) >= 200 else sum(cls) / len(cls)
            sma20_rise = (sum(cls[-5:]) / 5) > (sum(cls[-10:-5]) / 5)
            gains  = [max(cls[i] - cls[i-1], 0) for i in range(1, len(cls))]
            losses = [max(cls[i-1] - cls[i], 0) for i in range(1, len(cls))]
            ag = sum(gains[-14:])  / 14 if len(gains)  >= 14 else 0
            al = sum(losses[-14:]) / 14 if len(losses) >= 14 else 1
            rsi = 100 - (100 / (1 + ag / al))
            base5  = cls[-6] if len(cls) >= 6 else cls[0]
            ret5d  = round((cur - base5) / base5 * 100, 2) if base5 else 0
            avg20v = sum(vols[-20:]) / 20 if len(vols) >= 20 else 0
            avg5v  = sum(vols[-5:])  / 5  if len(vols) >= 5  else 0
            vol_surge  = bool(avg20v and avg5v > avg20v * 1.1)
            high20     = max(cls[-20:])
            near_high  = cur >= high20 * 0.95
            ema12      = calc_ema(cls[-30:], 12) if len(cls) >= 30 else cur
            ema26      = calc_ema(cls[-50:], 26) if len(cls) >= 50 else cur
            macd_bull  = ema12 > ema26
            golden     = sma20 > sma50
            above200   = cur > sma200
            macd_series = []
            for j in range(14, -1, -1):
                eidx = len(cls) - j
                if eidx >= 26:
                    sl = cls[max(0, eidx - 60):eidx]
                    macd_series.append(calc_ema(sl, 12) - calc_ema(sl, 26))
            if len(macd_series) >= 9:
                macd_hist_bull = macd_series[-1] > calc_ema(macd_series, 9)
            else:
                macd_hist_bull = macd_bull
            consec_up = (len(cls) >= 3 and cls[-1] > cls[-2] and cls[-2] > cls[-3])
            score = sum([
                cur > sma20, sma20_rise, cur > sma50, 40 <= rsi <= 65,
                ret5d > 0, vol_surge, near_high, golden, above200,
                macd_hist_bull, consec_up,
            ])
            if score >= 6:
                rows.append({
                    "Stock": nse, "Company": name, "Sector": SECTOR.get(nse, "Other"),
                    "Price (₹)": round(cur, 2), "5D Ret (%)": ret5d,
                    "RSI": round(rsi, 1), "Vol Surge": "Yes" if vol_surge else "No",
                    "Near High": "Yes" if near_high else "No",
                    "SMA Align": "Yes" if golden else "No",
                    "SMA200": "Yes" if above200 else "No",
                    "MACD Hist": "Yes" if macd_hist_bull else "No",
                    "Consec Up": "Yes" if consec_up else "No",
                    "Score /11": score,
                    "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{nse}",
                })
        except Exception:
            pass
    df = (pd.DataFrame(rows)
          .sort_values(["Score /11", "5D Ret (%)"], ascending=[False, False])
          .head(20).reset_index(drop=True))
    df.index += 1
    return df

# ── Screener 2: Support Entry ─────────────────────────────────────────────────
def run_support_entry(fno, close_df, low_df, high_df, vol_df):
    rows = []
    for _, nse, _ in fno:
        try:
            tk   = f"{nse}.NS"
            cs   = close_df[tk].dropna()
            c    = list(cs.astype(float))
            l    = list(low_df[tk].dropna().astype(float))
            hs   = list(high_df[tk].dropna().astype(float))
            v    = list(vol_df[tk].reindex(cs.index).fillna(0).astype(float))
            if len(c) < 30:
                continue
            p = c[-1]
            slows = []
            st = max(3, len(l) - 60)
            for si in range(st, len(l) - 3):
                if (all(l[si] <= l[si - k] for k in range(1, 4) if si - k >= 0)
                        and all(l[si] <= l[si + k] for k in range(1, 4))):
                    slows.append(l[si])
            sm20  = sum(c[-20:]) / 20
            sm50  = sum(c[-min(50, len(c)):]) / min(50, len(c))
            sm200 = sum(c[-200:]) / 200 if len(c) >= 200 else None
            sups  = [s for s in slows if s <= p * 1.03]
            for sm in [sm20, sm50, sm200]:
                if sm and sm <= p * 1.03:
                    sups.append(sm)
            if not sups:
                continue
            near = max(sups)
            gap  = (p - near) / near * 100
            if not (0 <= gap <= 3.0):
                continue
            hi20 = max(hs[-20:]) if len(hs) >= 20 else max(hs)
            pb   = (hi20 - p) / hi20 * 100
            if pb < 4:
                continue
            gains  = [max(c[i] - c[i-1], 0) for i in range(1, len(c))]
            losses = [max(c[i-1] - c[i], 0) for i in range(1, len(c))]
            ag = sum(gains[-14:])  / 14 if len(gains)  >= 14 else 0
            al = sum(losses[-14:]) / 14 if len(losses) >= 14 else 1
            rsi    = 100 - (100 / (1 + ag / al))
            bounce = len(c) >= 3 and c[-1] > c[-2] and c[-2] > c[-3]
            dayup  = c[-1] > c[-2]
            avgv   = sum(v[-20:]) / 20 if len(v) >= 20 else 0
            bvol   = bool(avgv and v[-1] > avgv * 1.1)
            if sm200 and abs(near - sm200) / sm200 < 0.012:
                stype = "SMA 200"
            elif abs(near - sm50) / sm50 < 0.012:
                stype = "SMA 50"
            elif abs(near - sm20) / sm20 < 0.012:
                stype = "SMA 20"
            else:
                stype = "Swing Low"
            sma50_20ago    = sum(c[-70:-20]) / 50 if len(c) >= 70 else None
            prior_up       = bool(sma50_20ago and sm50 >= sma50_20ago)
            sup_touches    = sum(1 for li in l[-120:] if abs(li - near) / near <= 0.02)
            score = sum([
                gap <= 1.5, bounce, dayup and bvol, 25 <= rsi <= 58,
                4 <= pb <= 20, pb >= 7, prior_up, sup_touches >= 2,
            ])
            if score >= 4:
                buy_lo = round(near * 0.99, 2)
                buy_hi = round(near * 1.02, 2)
                stop   = round(near * 0.97, 2)
                tgt    = round(hi20, 2)
                rwd    = round((tgt - p) / p * 100, 1)
                rsk    = round((p - stop) / p * 100, 1)
                rr     = round(rwd / rsk, 1) if rsk > 0 else 0.0
                rows.append({
                    "Stock": nse, "Company": COMPANY_NAMES.get(nse, nse),
                    "Sector": SECTOR.get(nse, "Other"),
                    "Price (₹)": round(p, 2), "Support (₹)": round(near, 2),
                    "Support Type": stype, "Sup. Touches": sup_touches,
                    "Gap %": round(gap, 2), "Pullback %": round(pb, 1),
                    "RSI": round(rsi, 1), "Prior Trend": "Yes" if prior_up else "No",
                    "Bounce": "Yes" if bounce else ("Up" if dayup else "No"),
                    "Vol Surge": "Yes" if bvol else "No",
                    "Buy Zone": f"₹{buy_lo}–{buy_hi}",
                    "Target (₹)": tgt, "Stop (₹)": stop,
                    "Risk %": rsk, "R:R": rr, "Score /8": score,
                    "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{nse}",
                })
        except Exception:
            pass
    df = (pd.DataFrame(rows)
          .sort_values(["Score /8", "R:R", "Gap %"], ascending=[False, False, True])
          .head(20).reset_index(drop=True))
    df.index += 1
    return df

# ── Screener 3: Consolidation Breakout ────────────────────────────────────────
def run_consolidation(fno, close_df, high_df, vol_df):
    rows = []
    for _, nse, _ in fno:
        try:
            tk  = f"{nse}.NS"
            cs  = close_df[tk].dropna()
            c   = list(cs.astype(float))
            h   = list(high_df[tk].dropna().astype(float))
            v   = list(vol_df[tk].reindex(cs.index).fillna(0).astype(float))
            if len(c) < 35:
                continue
            p = c[-1]
            range10 = (max(c[-10:]) - min(c[-10:])) / p * 100
            range30 = (max(c[-30:]) - min(c[-30:])) / p * 100
            sma50_pre = sum(c[-min(50, len(c)):]) / min(50, len(c))
            if range10 > 5 or c[-1] <= sma50_pre:
                continue
            range_contract = range10 < range30 * 0.50
            days_consol = 10
            for ext in range(11, min(60, len(c))):
                r_ext = (max(c[-ext:]) - min(c[-ext:])) / p * 100
                if r_ext > 6:
                    break
                days_consol = ext
            sma20    = sum(c[-20:]) / 20
            std20    = (sum((x - sma20) ** 2 for x in c[-20:]) / 20) ** 0.5
            bb_w     = 4 * std20 / sma20 * 100
            sma20_p  = sum(c[-35:-15]) / 20
            std20_p  = (sum((x - sma20_p) ** 2 for x in c[-35:-15]) / 20) ** 0.5
            bb_w_p   = 4 * std20_p / sma20_p * 100
            bb_sq    = bb_w < bb_w_p * 0.8
            high20   = max(h[-20:]) if len(h) >= 20 else max(h)
            near_hi  = p >= high20 * 0.95
            avgv5    = sum(v[-5:])  / 5  if len(v) >= 5  else 0
            avgv20   = sum(v[-20:]) / 20 if len(v) >= 20 else 0
            vol_dry  = bool(avgv20 and avgv5 < avgv20 * 0.85)
            vol_ratio = round(avgv5 / avgv20, 2) if avgv20 else 1.0
            sma20_5d = sum(c[-25:-5]) / 20 if len(c) >= 25 else sma20
            sma_flat = abs(sma20 - sma20_5d) / sma20 < 0.012
            above_sma20 = p > sma20
            sma50_20ago = sum(c[-70:-20]) / 50 if len(c) >= 70 else None
            prior_up    = bool(sma50_20ago and sma50_pre >= sma50_20ago)
            brk         = round(max(h[-10:]) * 1.005, 2)
            pct_to_brk  = round((brk - p) / p * 100, 2)
            score = sum([
                range10 < 3.5, range_contract, bb_sq, near_hi,
                vol_dry, sma_flat, above_sma20, prior_up,
            ])
            if score >= 5:
                rows.append({
                    "Stock": nse, "Company": COMPANY_NAMES.get(nse, nse),
                    "Sector": SECTOR.get(nse, "Other"),
                    "Price (₹)": round(p, 2), "Breakout ₹": brk,
                    "To Breakout%": pct_to_brk, "Days Consol.": days_consol,
                    "10D Range %": round(range10, 2), "BB Width %": round(bb_w, 2),
                    "Vol Ratio": vol_ratio,
                    "SMA Flat": "Yes" if sma_flat else "No",
                    "Near High": "Yes" if near_hi else "No",
                    "BB Squeeze": "Yes" if bb_sq else "No",
                    "Prior Trend": "Yes" if prior_up else "No",
                    "Score /8": score,
                    "Chart": f"https://www.tradingview.com/chart/?symbol=NSE:{nse}",
                })
        except Exception:
            pass
    df = (pd.DataFrame(rows)
          .sort_values(["Score /8", "Days Consol.", "10D Range %"],
                       ascending=[False, False, True])
          .head(20).reset_index(drop=True))
    df.index += 1
    return df

# ── Excel export with formatting ──────────────────────────────────────────────
def write_excel(sheets_data):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    HEADER_FILL  = PatternFill("solid", fgColor="1D4ED8")
    HEADER_FONT  = Font(color="FFFFFF", bold=True, size=10)
    GREEN_FILL   = PatternFill("solid", fgColor="D1FAE5")
    YELLOW_FILL  = PatternFill("solid", fgColor="FEF9C3")
    ALT_FILL     = PatternFill("solid", fgColor="F8FAFC")
    THIN         = Side(style="thin", color="E2E8F0")
    CELL_BORDER  = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    SCORE_COLS   = {"Score /11", "Score /8", "Score /6"}

    wb = Workbook()
    wb.remove(wb.active)  # remove default sheet

    tab_colors = {"Probable Upside": "3B82F6", "Support Entry": "10B981",
                  "Consolidation Breakout": "8B5CF6"}

    for sheet_name, df in sheets_data.items():
        ws = wb.create_sheet(title=sheet_name[:31])
        ws.sheet_properties.tabColor = tab_colors.get(sheet_name, "3B82F6")

        if df.empty:
            ws["A1"] = "No results found for this screener."
            continue

        cols = list(df.columns)

        # Header row
        for ci, col in enumerate(cols, start=1):
            cell = ws.cell(row=1, column=ci, value=col)
            cell.fill   = HEADER_FILL
            cell.font   = HEADER_FONT
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = CELL_BORDER

        ws.row_dimensions[1].height = 28

        # Data rows
        score_col_idx = next((ci + 1 for ci, c in enumerate(cols) if c in SCORE_COLS), None)
        max_score = df[next((c for c in cols if c in SCORE_COLS), cols[-1])].max() if score_col_idx else 0

        for ri, (_, row) in enumerate(df.iterrows(), start=2):
            row_fill = ALT_FILL if ri % 2 == 0 else None
            for ci, col in enumerate(cols, start=1):
                val  = row[col]
                cell = ws.cell(row=ri, column=ci, value=val)
                cell.border = CELL_BORDER
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if row_fill:
                    cell.fill = row_fill
                # Color score column
                if score_col_idx and ci == score_col_idx and isinstance(val, (int, float)):
                    cell.fill = GREEN_FILL if val >= max_score - 1 else YELLOW_FILL
                    cell.font = Font(bold=True, size=10)

        # Auto column width
        for ci, col in enumerate(cols, start=1):
            max_len = len(str(col))
            for ri in range(2, ws.max_row + 1):
                v = ws.cell(row=ri, column=ci).value
                max_len = max(max_len, len(str(v)) if v is not None else 0)
            ws.column_dimensions[get_column_letter(ci)].width = min(max_len + 3, 30)

        ws.freeze_panes = "A2"

    # Summary sheet
    ws_sum = wb.create_sheet(title="Summary", index=0)
    ws_sum.sheet_properties.tabColor = "0F172A"
    summary_rows = [
        ["NSE F&O Screener — Daily Export"],
        ["Generated", NOW],
        [""],
    ]
    for name, df in sheets_data.items():
        summary_rows.append([name, f"{len(df)} stocks found"])
    for ri, row in enumerate(summary_rows, start=1):
        for ci, val in enumerate(row, start=1):
            cell = ws_sum.cell(row=ri, column=ci, value=val)
            if ri == 1:
                cell.font = Font(bold=True, size=13, color="1D4ED8")
            elif ri >= 4:
                cell.font = Font(size=10)
    ws_sum.column_dimensions["A"].width = 30
    ws_sum.column_dimensions["B"].width = 20

    wb.save(OUTFILE)

# ── Consolidated 20-day history ───────────────────────────────────────────────
def update_consolidated_history(results: dict):
    """
    Appends today's screener results to consolidated_history.xlsx.
    Layout per sheet: Stock | Company | date1 | date2 | … (newest right)
    Keeps only the last 20 days of date columns.
    """
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    today_str = str(datetime.date.today())
    cutoff    = datetime.date.today() - datetime.timedelta(days=365)

    SCORE_COL = {
        "Probable Upside":        "Score /11",
        "Support Entry":          "Score /8",
        "Consolidation Breakout": "Score /8",
    }
    MAX_SCORE = {
        "Probable Upside": 11,
        "Support Entry":   8,
        "Consolidation Breakout": 8,
    }

    # ── Load existing history ──────────────────────────────────────────────────
    # history[sheet] = {stock: {"company": str, "scores": {date_str: "n/m"}}}
    history = {name: {} for name in results}

    if os.path.exists(HIST_FILE):
        try:
            wb_old = load_workbook(HIST_FILE)
            for sheet_name in results:
                if sheet_name not in wb_old.sheetnames:
                    continue
                ws = wb_old[sheet_name]
                headers = [cell.value for cell in ws[1]]
                date_cols = {}          # col_index (0-based) -> date_str
                for ci, h in enumerate(headers):
                    if h and h != "Stock":
                        try:
                            d = datetime.date.fromisoformat(str(h)[:10])
                            if d >= cutoff:
                                date_cols[ci] = str(d)
                        except Exception:
                            pass
                for row in ws.iter_rows(min_row=2, values_only=True):
                    stock = str(row[0]).strip() if row[0] else None
                    if not stock or stock == "None":
                        continue
                    entry = history[sheet_name].setdefault(
                        stock, {"scores": {}}
                    )
                    for ci, date_str in date_cols.items():
                        if ci < len(row) and row[ci]:
                            entry["scores"][date_str] = str(row[ci])
        except Exception:
            pass   # corrupt file — rebuild from scratch

    # ── Merge today's results ──────────────────────────────────────────────────
    for sheet_name, df in results.items():
        if df is None or df.empty:
            continue
        scol  = SCORE_COL.get(sheet_name, "Score /8")
        mscore = MAX_SCORE.get(sheet_name, 8)
        for _, row in df.iterrows():
            stock   = str(row.get("Stock", "")).strip()
            score   = row.get(scol, "")
            if not stock:
                continue
            entry = history[sheet_name].setdefault(stock, {"scores": {}})
            try:
                entry["scores"][today_str] = f"{int(score)}/{mscore}"
            except Exception:
                entry["scores"][today_str] = str(score)

    # ── Build workbook ─────────────────────────────────────────────────────────
    HDR_FILL   = PatternFill("solid", fgColor="1F497D")
    HDR_FONT   = Font(bold=True, color="FFFFFF", size=10)
    DATE_FILL  = PatternFill("solid", fgColor="2E75B6")
    DATE_FONT  = Font(bold=True, color="FFFFFF", size=10)
    GREEN_FILL = PatternFill("solid", fgColor="C6EFCE")
    YLLOW_FILL = PatternFill("solid", fgColor="FFEB9C")
    ALT_FILL   = PatternFill("solid", fgColor="EEF3FB")
    CENTER     = Alignment(horizontal="center", vertical="center")
    THIN       = Border(
        left   = Side(style="thin", color="D0D0D0"),
        right  = Side(style="thin", color="D0D0D0"),
        top    = Side(style="thin", color="D0D0D0"),
        bottom = Side(style="thin", color="D0D0D0"),
    )
    TAB_COLORS = {
        "Probable Upside":        "4472C4",
        "Support Entry":          "70AD47",
        "Consolidation Breakout": "ED7D31",
    }

    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, stock_data in history.items():
        if not stock_data:
            continue

        all_dates = sorted(
            {d for e in stock_data.values() for d in e["scores"]
             if datetime.date.fromisoformat(d) >= cutoff}
        )

        ws = wb.create_sheet(sheet_name)
        ws.sheet_properties.tabColor = TAB_COLORS.get(sheet_name, "4472C4")
        ws.freeze_panes = "B2"

        # Header row
        for ci, h in enumerate(["Stock"] + all_dates, 1):
            cell = ws.cell(row=1, column=ci, value=h)
            cell.font      = DATE_FONT if ci > 1 else HDR_FONT
            cell.fill      = DATE_FILL if ci > 1 else HDR_FILL
            cell.alignment = CENTER
            cell.border    = THIN
        ws.row_dimensions[1].height = 22

        # Sort: today's score desc, then alphabetical
        def _sort_key(item):
            scr = item[1]["scores"].get(today_str, "")
            try:
                return (-int(scr.split("/")[0]), item[0])
            except Exception:
                return (0, item[0])

        for ri, (stock, entry) in enumerate(sorted(stock_data.items(), key=_sort_key), 2):
            alt_fill = ALT_FILL if ri % 2 == 0 else None

            c = ws.cell(row=ri, column=1, value=stock)
            c.font = Font(bold=True, size=10); c.border = THIN; c.alignment = Alignment(vertical="center")
            if alt_fill: c.fill = alt_fill

            for ci, date_str in enumerate(all_dates, 2):
                val = entry["scores"].get(date_str, "")
                c = ws.cell(row=ri, column=ci, value=val)
                c.alignment = CENTER; c.border = THIN; c.font = Font(size=10)
                if val:
                    try:
                        ratio = int(val.split("/")[0]) / int(val.split("/")[1])
                        c.fill = GREEN_FILL if ratio >= 0.75 else YLLOW_FILL
                    except Exception:
                        c.fill = YLLOW_FILL
                elif alt_fill:
                    c.fill = alt_fill

        ws.column_dimensions["A"].width = 18
        for ci in range(2, len(all_dates) + 2):
            ws.column_dimensions[get_column_letter(ci)].width = 13

    wb.save(HIST_FILE)

# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    log("NSE F&O Daily Export starting…")

    fno_live, fno_cached_names, fno_source = fetch_fno_symbols()
    COMPANY_NAMES_MERGED = {**fno_cached_names, **COMPANY_NAMES}
    FNO = (
        [(s, s, COMPANY_NAMES_MERGED.get(s, s)) for s in fno_live]
        if fno_live
        else [(s, s, n) for s, n in sorted(COMPANY_NAMES.items())]
    )
    log(f"F&O list: {len(FNO)} stocks ({fno_source})")

    tickers = [f"{s}.NS" for _, s, _ in FNO]

    log("Downloading 1Y price history for all stocks…")
    hist = yf.download(tickers, period="1y", auto_adjust=True, progress=False)
    close_df = hist["Close"]
    high_df  = hist["High"]
    low_df   = hist["Low"]
    vol_df   = hist["Volume"]
    log("Download complete. Running screeners…")

    df1 = run_probable_upside(FNO, close_df, vol_df)
    log(f"Probable Upside:        {len(df1)} candidates")

    df2 = run_support_entry(FNO, close_df, low_df, high_df, vol_df)
    log(f"Support Entry:          {len(df2)} candidates")

    df3 = run_consolidation(FNO, close_df, high_df, vol_df)
    log(f"Consolidation Breakout: {len(df3)} candidates")

    write_excel({
        "Probable Upside":        df1,
        "Support Entry":          df2,
        "Consolidation Breakout": df3,
    })
    log(f"Saved → {OUTFILE}")

    update_consolidated_history({
        "Probable Upside":        df1,
        "Support Entry":          df2,
        "Consolidation Breakout": df3,
    })
    log(f"History updated → {HIST_FILE}")

    # Cleanup: delete Excel files older than 20 days
    cutoff = datetime.date.today() - datetime.timedelta(days=20)
    deleted = []
    for fname in os.listdir(EXPORTS_DIR):
        if not fname.startswith("screener_") or not fname.endswith(".xlsx"):
            continue
        try:
            file_date = datetime.date.fromisoformat(fname[9:19])  # screener_YYYY-MM-DD.xlsx
            if file_date < cutoff:
                os.remove(os.path.join(EXPORTS_DIR, fname))
                deleted.append(fname)
        except Exception:
            pass
    if deleted:
        log(f"Deleted {len(deleted)} old file(s): {', '.join(deleted)}")

    # Cross-platform notification
    try:
        import platform, subprocess
        msg = (f"Screener export complete — "
               f"{len(df1)} upside, {len(df2)} support, {len(df3)} consolidation setups.")
        system = platform.system()
        if system == "Darwin":
            subprocess.run([
                "osascript", "-e",
                f'display notification "{msg}" with title "NSE F&O Export" sound name "Glass"'
            ], check=False)
        elif system == "Windows":
            subprocess.run([
                "powershell", "-Command",
                f'[System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms") | Out-Null;'
                f'[System.Windows.Forms.MessageBox]::Show("{msg}", "NSE F&O Export")'
            ], check=False)
        # Linux: notification not needed (headless server)
    except Exception:
        pass
