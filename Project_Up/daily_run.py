"""
Headless daily screener for Project Up.
Runs the same 5-step PVA pipeline as app.py — no Streamlit required.
Scheduled via cron at 15:00 Mon-Fri; output goes to daily_run.log.
"""
import sys, os, json, datetime
import pandas as pd
import requests, io

DIR = os.path.dirname(os.path.abspath(__file__))
UNIVERSE_CACHE = os.path.join(DIR, "universe_cache.json")
MCAP_CACHE     = os.path.join(DIR, "mcap_cache.json")
HIST_PATH      = os.path.join(DIR, "history.xlsx")
DAILY_TOP_PATH = os.path.join(DIR, "dailyTop.xlsx")

def _log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def _cache_age_days(data):
    try:
        return (datetime.date.today() - datetime.date.fromisoformat(data.get("updated", "2000-01-01"))).days
    except Exception:
        return 999

def _ema_series(prices, period):
    if len(prices) < period:
        return []
    k = 2.0 / (period + 1)
    val = sum(prices[:period]) / period
    out = [val]
    for p in prices[period:]:
        val = val * (1 - k) + p * k
        out.append(val)
    return out

def _ema_val(prices, period):
    s = _ema_series(prices, period)
    return s[-1] if s else None

def _rsi_wilder(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    gains  = [max(prices[i] - prices[i-1], 0) for i in range(1, len(prices))]
    losses = [max(prices[i-1] - prices[i], 0) for i in range(1, len(prices))]
    ag = sum(gains[:period])  / period
    al = sum(losses[:period]) / period
    for g, l in zip(gains[period:], losses[period:]):
        ag = (ag * (period - 1) + g) / period
        al = (al * (period - 1) + l) / period
    return 100 - (100 / (1 + ag / max(al, 1e-10)))

def _fetch_universe():
    cache = _load_json(UNIVERSE_CACHE)
    if cache.get("symbols") and _cache_age_days(cache) < 7:
        _log(f"Universe: {len(cache['symbols'])} stocks (cache)")
        return cache["symbols"], cache.get("names", {})
    try:
        r = requests.get(
            "https://archives.nseindia.com/content/equities/EQUITY_L.csv",
            timeout=25,
        )
        r.raise_for_status()
        df = pd.read_csv(io.StringIO(r.text))
        sym_col  = df.columns[0]
        name_col = next((c for c in df.columns if "NAME" in c.upper()), None)
        symbols  = sorted(str(s).strip() for s in df[sym_col].dropna() if str(s).strip())
        names    = {}
        if name_col:
            for _, row in df.iterrows():
                s = str(row[sym_col]).strip()
                n = str(row[name_col]).strip()
                if s and n and n.lower() != "nan":
                    names[s] = n.title()
        if len(symbols) >= 100:
            _save_json(UNIVERSE_CACHE, {
                "updated": str(datetime.date.today()),
                "symbols": symbols,
                "names": names,
            })
            _log(f"Universe: {len(symbols)} stocks (live NSE)")
            return symbols, names
    except Exception as e:
        _log(f"Universe fetch error: {e}")
    if cache.get("symbols"):
        _log(f"Universe: {len(cache['symbols'])} stocks (offline cache)")
        return cache["symbols"], cache.get("names", {})
    return [], {}

def _get_mcap(sym_ns, mcap_data):
    today = str(datetime.date.today())
    entry = mcap_data.get(sym_ns)
    if entry:
        try:
            age = (datetime.date.today() - datetime.date.fromisoformat(entry["date"])).days
            if age < 7:
                return entry["mcap"]
        except Exception:
            pass
    try:
        import yfinance as yf
        mc = yf.Ticker(sym_ns).fast_info.market_cap or 0
    except Exception:
        mc = 0
    mcap_data[sym_ns] = {"mcap": mc, "date": today}
    return mc

def _find_streak_stocks(sheets: dict, min_streak: int = 2) -> dict:
    """Return {stock: set_of_date_strings} for stocks in ≥ min_streak consecutive date sheets."""
    all_dates = sorted(sheets.keys())
    stock_indices: dict = {}
    for ci, d in enumerate(all_dates):
        df = sheets[d]
        if df is None or df.empty or "Stock" not in df.columns:
            continue
        for stock in df["Stock"].astype(str).str.strip():
            if stock and stock != "nan":
                stock_indices.setdefault(stock, []).append(ci)

    streak_dates: dict = {}
    for stock, indices in stock_indices.items():
        indices = sorted(set(indices))
        streak = [indices[0]]
        for i in range(1, len(indices)):
            if indices[i] == indices[i - 1] + 1:
                streak.append(indices[i])
            else:
                if len(streak) >= min_streak:
                    for idx in streak:
                        streak_dates.setdefault(stock, set()).add(all_dates[idx])
                streak = [indices[i]]
        if len(streak) >= min_streak:
            for idx in streak:
                streak_dates.setdefault(stock, set()).add(all_dates[idx])
    return streak_dates


def _write_formatted_excel(path, sheets, streak_stocks=None):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HDR_FILL    = PatternFill("solid", fgColor="1D4ED8")
    HDR_FONT    = Font(color="FFFFFF", bold=True, size=10)
    ALT_FILL    = PatternFill("solid", fgColor="EFF6FF")
    SCR_HI      = PatternFill("solid", fgColor="D1FAE5")
    SCR_MED     = PatternFill("solid", fgColor="FEF9C3")
    STREAK_FILL = PatternFill("solid", fgColor="FFD580")  # warm orange — 2+ consecutive days
    THIN        = Side(style="thin", color="E2E8F0")
    BORDER      = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    CENTER      = Alignment(horizontal="center", vertical="center")
    wb = Workbook()
    wb.remove(wb.active)
    for sheet_name, df in sheets.items():
        ws = wb.create_sheet(title=sheet_name[:31])
        if df.empty:
            ws["A1"] = "No data"; continue
        cols = list(df.columns)
        for ci, col in enumerate(cols, 1):
            c = ws.cell(row=1, column=ci, value=col)
            c.fill = HDR_FILL; c.font = HDR_FONT
            c.alignment = CENTER; c.border = BORDER
        ws.row_dimensions[1].height = 24
        ws.freeze_panes = "A2"
        for ri, (_, row) in enumerate(df.iterrows(), 2):
            stock_val = str(row.get("Stock", "")).strip() if "Stock" in row else ""
            is_streak = bool(
                streak_stocks and stock_val
                and sheet_name in streak_stocks.get(stock_val, set())
            )
            for ci, col in enumerate(cols, 1):
                val = row[col]
                c = ws.cell(row=ri, column=ci, value=val)
                c.border = BORDER; c.alignment = CENTER
                if is_streak:
                    c.fill = STREAK_FILL
                    c.font = Font(bold=True, size=10, color="7D3C00")
                else:
                    if ri % 2 == 0:
                        c.fill = ALT_FILL
                    if col in ("Score /10", "Score /9", "Score"):
                        try:
                            sv = float(val)
                            c.fill = SCR_HI if sv >= 7 else SCR_MED
                            c.font = Font(bold=True, size=10)
                        except (TypeError, ValueError):
                            pass
        for ci, col in enumerate(cols, 1):
            ml = max((len(str(ws.cell(r, ci).value or "")) for r in range(1, ws.max_row + 1)), default=8)
            ws.column_dimensions[get_column_letter(ci)].width = min(ml + 3, 28)
    wb.save(path)

def _save_history(rows, top_n=15, keep_days=60, prefix="", sort_cols=None):
    if not rows:
        return
    d = datetime.date.today()
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    today = prefix + str(d)

    df = pd.DataFrame(rows)
    if sort_cols is None:
        sort_cols = ["Score /10", "Vol Ratio", "Mkt Cap (Cr)"]
    valid_sort = [c for c in sort_cols if c in df.columns]
    df_new = df.sort_values(valid_sort, ascending=False).head(top_n).astype(str)

    # Load existing sheets — keep only those matching the same prefix
    existing = {}
    if os.path.exists(HIST_PATH):
        try:
            xl = pd.ExcelFile(HIST_PATH)
            for sheet in xl.sheet_names:
                if sheet.startswith(prefix):
                    existing[sheet] = xl.parse(sheet, dtype=str)
        except Exception:
            pass

    existing[today] = df_new

    # Keep last keep_days sheets for this prefix
    sorted_dates = sorted(existing.keys())[-keep_days:]
    sheets_this  = {d: existing[d] for d in sorted_dates}

    # Streak detection only for upside (plain date prefix)
    streak_stocks = _find_streak_stocks(sheets_this, min_streak=2) if not prefix else None

    # Merge with other-prefix sheets already in the file
    all_sheets = {}
    if os.path.exists(HIST_PATH):
        try:
            xl2 = pd.ExcelFile(HIST_PATH)
            for sheet in xl2.sheet_names:
                if not sheet.startswith(prefix):
                    all_sheets[sheet] = xl2.parse(sheet, dtype=str)
        except Exception:
            pass
    all_sheets.update(sheets_this)

    _write_formatted_excel(HIST_PATH, all_sheets, streak_stocks=streak_stocks)
    _log(f"Saved {len(df_new)} rows to history.xlsx (sheet: {today}, prefix='{prefix}', {len(sheets_this)} dates stored)")

def _save_daily_top(all_close, names, top_n=30, keep_days=30):
    today = datetime.date.today()
    while today.weekday() >= 5:
        today -= datetime.timedelta(days=1)
    date_str = str(today)

    rows = []
    for sym_ns, c in all_close.items():
        if len(c) < 2:
            continue
        price = c[-1]
        prev  = c[-2]
        if prev <= 0 or price < 10:
            continue
        chg_pct = round((price - prev) / prev * 100, 2)
        # Skip data artefacts: yfinance dropna() can skip circuit-hit days,
        # making c[-2] several sessions old and inflating the % change.
        # India's standard daily circuit limit is ±20%.
        if abs(chg_pct) > 20:
            continue
        sym = sym_ns.replace(".NS", "")
        rows.append({"Stock": sym, "Change %": chg_pct, "Price (₹)": round(price, 2)})

    if not rows:
        _log("Daily Top: no data to save")
        return

    df_today = (pd.DataFrame(rows)
                .sort_values("Change %", ascending=False)
                .head(top_n)
                .reset_index(drop=True))
    df_today.index += 1

    # Load existing sheets, add today's, keep last keep_days
    existing = {}
    if os.path.exists(DAILY_TOP_PATH):
        try:
            xl = pd.ExcelFile(DAILY_TOP_PATH)
            for sheet in xl.sheet_names:
                existing[sheet] = xl.parse(sheet)
        except Exception:
            pass

    existing[date_str] = df_today

    # Keep only the most recent keep_days sheets (sorted by date)
    sorted_dates = sorted(existing.keys())[-keep_days:]
    sheets_to_save = {d: existing[d] for d in sorted_dates}

    _write_formatted_excel(DAILY_TOP_PATH, sheets_to_save)
    _log(f"Daily Top saved → {DAILY_TOP_PATH}  ({len(sheets_to_save)} dates stored)")


def _scan_bottom(all_close, all_high, all_low, all_vol, names, mcap_data):
    """Run Bottom Formation scan and save top 20 to history with 'B-' prefix."""
    rows = []
    candidates = [
        k for k, v in mcap_data.items()
        if isinstance(v, dict) and 5_000_000_000 <= v.get("mcap", 0) < 500_000_000_000
        and k in all_close
    ]
    _log(f"Bottom Formation scan: {len(candidates)} candidates")
    for sym_ns in candidates:
        try:
            c = all_close[sym_ns]
            h = all_high.get(sym_ns, c)
            l = all_low.get(sym_ns, c)
            v = all_vol.get(sym_ns, [])
            if len(c) < 100 or len(h) < 15 or len(l) < 15:
                continue
            price  = c[-1]
            high52 = max(h[-252:]) if len(h) >= 252 else max(h)
            low52  = min(l[-252:]) if len(l) >= 252 else min(l)
            pct_off_high = (price - high52) / high52 * 100
            if not (-55 <= pct_off_high <= -20):
                continue
            bounce_from_low = (price - low52) / low52 * 100
            if bounce_from_low < 7:
                continue
            rsi_now = _rsi_wilder(c)
            if not (40 <= rsi_now <= 65):
                continue
            lookback_low       = min(60, len(l) - 1)
            sub_l              = l[-lookback_low:]
            recent_low_val     = min(sub_l)
            recent_low_sub_idx = len(sub_l) - 1 - sub_l[::-1].index(recent_low_val)
            days_since_low     = (len(sub_l) - 1) - recent_low_sub_idx
            recent_low_global  = len(c) - lookback_low + recent_low_sub_idx
            rsi_at_low = _rsi_wilder(c[:recent_low_global + 1]) if recent_low_global >= 15 else 50
            rsi_div    = rsi_now - rsi_at_low
            if rsi_div < 5 or rsi_at_low >= 42:
                continue
            if not (l[-1] > l[-8] and min(l[-5:]) > l[-15]):
                continue
            vol_dry = False
            if len(v) >= 30:
                avg_base  = sum(v[-15:]) / 15
                avg_prior = sum(v[-45:-15]) / 30 if len(v) >= 45 else sum(v[-30:-15]) / 15
                vol_dry   = avg_base < avg_prior * 0.85
            e200 = _ema_val(c, 200) if len(c) >= 200 else None
            pct_from_e200  = round((price - e200) / e200 * 100, 1) if e200 else None
            approaching_ema = e200 is not None and -12 <= pct_from_e200 <= 3
            score = sum([
                vol_dry, rsi_div > 15, bounce_from_low > 15, days_since_low <= 25,
                approaching_ema, rsi_now > 50, min(l[-5:]) > recent_low_val * 1.03,
                len(v) >= 5 and v[-1] > sum(v[-6:-1]) / 5, pct_off_high >= -35,
            ])
            if score < 3:
                continue
            sym = sym_ns.replace(".NS", "")
            rows.append({
                "Stock":           sym,
                "Company":         names.get(sym, sym),
                "Price (₹)":      round(price, 2),
                "% off Peak":      round(pct_off_high, 1),
                "Bounce from Low": round(bounce_from_low, 1),
                "RSI":             round(rsi_now, 1),
                "RSI at Low":      round(rsi_at_low, 1),
                "RSI Divergence":  round(rsi_div, 1),
                "Days Since Low":  days_since_low,
                "Vol Dry-up":      "Yes" if vol_dry else "No",
                "% from 200 EMA":  pct_from_e200,
                "Score /9":        score,
                "Mkt Cap (Cr)":    round(mcap_data[sym_ns]["mcap"] / 1e7),
            })
        except Exception:
            pass
    _log(f"Bottom Formation: {len(rows)} setups found")
    return rows


def _scan_consol(all_close, all_high, all_low, all_vol, names, mcap_data):
    """Run Consolidation scan and save top 20 to history with 'C-' prefix."""
    rows = []
    candidates = [
        k for k, v in mcap_data.items()
        if isinstance(v, dict) and 5_000_000_000 <= v.get("mcap", 0) < 500_000_000_000
        and k in all_close
    ]
    _log(f"Consolidation scan: {len(candidates)} candidates")
    for sym_ns in candidates:
        try:
            c = all_close[sym_ns]
            h = all_high.get(sym_ns, c)
            l = all_low.get(sym_ns, c)
            v = all_vol.get(sym_ns, [])
            if len(c) < 60 or len(h) < 20 or len(l) < 20:
                continue
            price = c[-1]
            e50   = _ema_val(c, 50)
            e20   = _ema_val(c, 20)
            e200  = _ema_val(c, 200) if len(c) >= 200 else None
            if not e50 or not e20:
                continue
            if price < e50:
                continue
            rsi = _rsi_wilder(c)
            if not (44 <= rsi <= 66):
                continue
            range_20d = (max(h[-20:]) - min(l[-20:])) / price * 100
            if range_20d > 10:
                continue
            range_10d    = (max(h[-10:]) - min(l[-10:])) / price * 100
            range_prev10 = (max(h[-20:-10]) - min(l[-20:-10])) / price * 100
            coiling      = range_10d < range_prev10
            vol_dry = False
            if len(v) >= 40:
                avg_consol = sum(v[-20:]) / 20
                avg_prior  = sum(v[-40:-20]) / 20
                vol_dry    = avg_prior > 0 and avg_consol < avg_prior * 0.80
            prior_up      = len(c) >= 45 and c[-20] > c[-45]
            high52        = max(h[-252:]) if len(h) >= 252 else max(h)
            pct_from_high = (price - high52) / high52 * 100
            if pct_from_high < -25:
                continue
            if price < e20 * 0.97:
                continue
            above_200         = e200 and price > e200
            at_ema_support    = (abs(price / e20 - 1) <= 0.02 or abs(price / e50 - 1) <= 0.02)
            consecutive_tight = range_10d < 5
            score = sum([
                vol_dry, coiling, consecutive_tight, prior_up, bool(above_200),
                rsi >= 52, at_ema_support, pct_from_high >= -10,
                len(v) >= 5 and v[-1] < sum(v[-6:-1]) / 5,
            ])
            if score < 4:
                continue
            pct_from_e200 = round((price - e200) / e200 * 100, 1) if e200 else None
            sym = sym_ns.replace(".NS", "")
            rows.append({
                "Stock":          sym,
                "Company":        names.get(sym, sym),
                "Price (₹)":     round(price, 2),
                "Range 20D %":    round(range_20d, 1),
                "Range 10D %":    round(range_10d, 1),
                "Coiling":        "Yes" if coiling else "No",
                "RSI":            round(rsi, 1),
                "Vol Dry-up":     "Yes" if vol_dry else "No",
                "% from 200 EMA": pct_from_e200,
                "% from High":    round(pct_from_high, 1),
                "Score /9":       score,
                "Mkt Cap (Cr)":   round(mcap_data[sym_ns]["mcap"] / 1e7),
            })
        except Exception:
            pass
    _log(f"Consolidation: {len(rows)} setups found")
    return rows


def _write_section(ws, title, rows, row_start, sec_color):
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    if not rows:
        return row_start

    HDR_FILL = PatternFill("solid", fgColor="1D4ED8")
    HDR_FONT = Font(color="FFFFFF", bold=True, size=10)
    ALT_FILL = PatternFill("solid", fgColor="EFF6FF")
    SCR_HI   = PatternFill("solid", fgColor="D1FAE5")
    SCR_MED  = PatternFill("solid", fgColor="FEF9C3")
    THIN     = Side(style="thin", color="E2E8F0")
    BORDER   = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
    CENTER   = Alignment(horizontal="center", vertical="center")
    SEC_FILL = PatternFill("solid", fgColor=sec_color)

    cols = [c for c in rows[0].keys() if c != "Chart"]
    n    = len(cols)

    # Section heading (merged across all columns)
    ws.merge_cells(start_row=row_start, start_column=1, end_row=row_start, end_column=n)
    c = ws.cell(row=row_start, column=1, value=f"  {title}")
    c.fill = SEC_FILL
    c.font = Font(color="FFFFFF", bold=True, size=11)
    c.alignment = Alignment(horizontal="left", vertical="center")
    ws.row_dimensions[row_start].height = 24
    row_start += 1

    # Column headers
    for ci, col in enumerate(cols, 1):
        c = ws.cell(row=row_start, column=ci, value=col)
        c.fill = HDR_FILL; c.font = HDR_FONT
        c.alignment = CENTER; c.border = BORDER
    ws.row_dimensions[row_start].height = 20
    row_start += 1

    # Data rows
    for ri, row in enumerate(rows):
        for ci, col in enumerate(cols, 1):
            val = row.get(col)
            c = ws.cell(row=row_start, column=ci, value=val)
            c.border = BORDER; c.alignment = CENTER
            if ri % 2 == 0:
                c.fill = ALT_FILL
            if col in ("Score /10", "Score /9"):
                try:
                    sv = float(val)
                    c.fill = SCR_HI if sv >= 7 else SCR_MED
                    c.font = Font(bold=True, size=10)
                except (TypeError, ValueError):
                    pass
        ws.row_dimensions[row_start].height = 18
        row_start += 1

    # Auto-fit column widths
    data_start = row_start - len(rows) - 1
    for ci, col in enumerate(cols, 1):
        ml = max(
            (len(str(ws.cell(r, ci).value or "")) for r in range(data_start, row_start)),
            default=8,
        )
        ws.column_dimensions[get_column_letter(ci)].width = min(ml + 3, 30)

    return row_start + 1  # blank separator


def _save_combined_history(upside_rows, bottom_rows, consol_rows, keep_days=60):
    from openpyxl import load_workbook, Workbook

    d = datetime.date.today()
    while d.weekday() >= 5:
        d -= datetime.timedelta(days=1)
    today = str(d)

    # Load or create workbook
    if os.path.exists(HIST_PATH):
        try:
            wb = load_workbook(HIST_PATH)
        except Exception:
            wb = Workbook()
    else:
        wb = Workbook()

    # Remove default empty sheet created by Workbook()
    for s in list(wb.sheetnames):
        ws = wb[s]
        if ws.max_row == 1 and ws.max_column == 1 and ws["A1"].value is None:
            del wb[s]
            break

    # Remove today's sheet + old B-/C- prefixed sheets from previous format
    for name in list(wb.sheetnames):
        if name == today or name.startswith("B-") or name.startswith("C-"):
            del wb[name]

    # Sort results
    u_rows = sorted(upside_rows, key=lambda x: (x.get("Score /10", 0), x.get("Vol Ratio", 0)), reverse=True)[:15]
    b_rows = sorted(bottom_rows, key=lambda x:  x.get("Score /9",  0), reverse=True)[:20]
    c_rows = sorted(consol_rows, key=lambda x:  x.get("Score /9",  0), reverse=True)[:20]

    ws = wb.create_sheet(title=today)
    ws.freeze_panes = "A2"

    row = 1
    row = _write_section(ws, f"UPSIDE SETUP  ({len(u_rows)} stocks)",       u_rows, row, "052e16")
    row = _write_section(ws, f"BOTTOM FORMATION  ({len(b_rows)} stocks)",   b_rows, row, "1e3a5f")
    row = _write_section(ws, f"CONSOLIDATION  ({len(c_rows)} stocks)",      c_rows, row, "3b1f5e")

    # Keep only last keep_days date sheets
    def _is_plain_date(name):
        try:
            datetime.date.fromisoformat(name)
            return True
        except ValueError:
            return False

    date_sheets = sorted(s for s in wb.sheetnames if _is_plain_date(s))
    for old in date_sheets[:-keep_days]:
        del wb[old]

    wb.save(HIST_PATH)
    _log(
        f"Combined history saved → {today}  "
        f"(Upside: {len(u_rows)}, Bottom: {len(b_rows)}, Consol: {len(c_rows)})"
    )


def run():
    import yfinance as yf

    _log("Project Up — daily screener starting")

    # ── Step 1: Universe ──────────────────────────────────────────────────────
    symbols, names = _fetch_universe()
    if not symbols:
        _log("ERROR: empty universe — aborting")
        sys.exit(1)

    tickers = [f"{s}.NS" for s in symbols]

    # ── Step 2: Batch OHLCVO download ─────────────────────────────────────────
    BATCH = 400
    all_close, all_high, all_low, all_vol, all_open = {}, {}, {}, {}, {}
    batches = [tickers[i:i+BATCH] for i in range(0, len(tickers), BATCH)]
    _log(f"Downloading {len(tickers)} tickers in {len(batches)} batches…")

    for bi, batch in enumerate(batches):
        _log(f"  Batch {bi+1}/{len(batches)} ({len(batch)} stocks)")
        try:
            dh = yf.download(batch, period="1y", auto_adjust=True, progress=False, threads=True)
            if dh.empty:
                continue
            for field, store in [("Close", all_close), ("High", all_high),
                                  ("Low", all_low), ("Volume", all_vol), ("Open", all_open)]:
                try:
                    sub = dh[field]
                except KeyError:
                    continue
                if isinstance(sub, pd.Series):
                    s = sub.dropna()
                    if len(s) >= 60:
                        store[batch[0]] = list(s.astype(float))
                else:
                    for col in sub.columns:
                        s = sub[col].dropna()
                        if len(s) >= 60:
                            store[col] = list(s.astype(float))
        except Exception as e:
            _log(f"  Batch {bi+1} error: {e}")

    # ── Step 3: 200 EMA filter ────────────────────────────────────────────────
    ema200_pass = [
        sym_ns for sym_ns, c in all_close.items()
        if len(c) >= 200 and _ema_val(c, 200) and c[-1] > _ema_val(c, 200)
    ]
    _log(f"200 EMA filter: {len(ema200_pass)} pass")

    # ── Step 4: Market cap filter ─────────────────────────────────────────────
    mcap_data = _load_json(MCAP_CACHE)
    mcap_pass = []
    for mi, sym_ns in enumerate(ema200_pass):
        mc = _get_mcap(sym_ns, mcap_data)
        if 10_000_000_000 <= mc < 2_000_000_000_000:
            mcap_pass.append((sym_ns, mc))
        if (mi + 1) % 100 == 0:
            _save_json(MCAP_CACHE, mcap_data)
            _log(f"  Mcap check {mi+1}/{len(ema200_pass)}: {len(mcap_pass)} qualifying")
    _save_json(MCAP_CACHE, mcap_data)
    _log(f"Mkt Cap filter: {len(mcap_pass)} pass")

    # ── Step 5: Score setup signals ───────────────────────────────────────────
    rows = []
    for sym_ns, mc in mcap_pass:
        try:
            sym = sym_ns.replace(".NS", "")
            c = all_close[sym_ns]
            h = all_high.get(sym_ns, [])
            l = all_low.get(sym_ns, [])
            v = all_vol.get(sym_ns, [])

            if len(c) < 60 or len(h) < 11 or len(l) < 11 or len(v) < 20:
                continue

            price = c[-1]
            e200  = _ema_val(c, 200)
            e20   = _ema_val(c, 20)
            e50   = _ema_val(c, 50)
            if not (e200 and e20 and e50):
                continue
            above_200_pct = round((price - e200) / e200 * 100, 1)

            avgv20    = sum(v[-20:]) / 20
            vol_ratio = round(v[-1] / avgv20, 2) if avgv20 else 0.0
            day_range = max(h[-1] - l[-1], 0.01)

            high52 = max(h[-252:]) if len(h) >= 252 else max(h)
            rsi14  = _rsi_wilder(c)
            if not (50 <= rsi14 <= 68):
                continue
            if price < high52 * 0.75:
                continue

            vol_dryup       = bool(avgv20 and v[-1] < avgv20 * 0.70)
            vcp_contraction = bool(len(v) >= 3 and v[-3] > v[-2] > v[-1])
            squeeze3        = bool(len(h) >= 3 and len(l) >= 3 and
                                   (max(h[-3:]) - min(l[-3:])) / price < 0.04)
            prior_up        = bool(len(c) >= 61 and c[-1] > c[-31] and c[-1] > c[-16] and c[-1] > c[-61])

            up_v10 = dn_v10 = 0.0
            for i in range(max(1, len(c) - 10), len(c)):
                if c[i] > c[i-1]:
                    up_v10 += v[i]
                else:
                    dn_v10 += v[i]
            net_accum = up_v10 > dn_v10 * 1.2

            weak_selling = True
            for i in range(max(1, len(c) - 5), len(c)):
                if c[i] < c[i-1] and avgv20 and v[i] >= avgv20 * 0.55:
                    weak_selling = False
                    break

            rising_lows    = bool(len(l) >= 7 and l[-1] > l[-4] and l[-4] > l[-7])
            avg_close_pos  = sum((c[i]-l[i])/max(h[i]-l[i], 0.01) for i in range(-3, 0)) / 3
            bullish_closes = avg_close_pos >= 0.55
            at_support     = ((-0.01 <= (price/e20 - 1) <= 0.02) or
                              (-0.01 <= (price/e50 - 1) <= 0.015))
            entry_trigger  = bool(len(v) >= 2 and len(c) >= 2 and
                                  v[-1] > v[-2] and c[-1] > c[-2])

            score = sum([vol_dryup, vcp_contraction, squeeze3, prior_up,
                         net_accum, weak_selling, rising_lows,
                         bullish_closes, at_support, entry_trigger])

            if score >= 6:
                low5   = min(l[-5:]) if len(l) >= 5 else l[-1]
                buy_lo = round(price * 0.995, 2)
                buy_hi = round(price * 1.005, 2)
                stop   = round(low5 * 0.99, 2)
                target = round(min(price * 1.07, high52 * 0.995), 2)
                risk   = round((price - stop) / price * 100, 1)
                reward = round((target - price) / price * 100, 1)
                rr     = round(reward / risk, 1) if risk > 0 else 0.0

                rows.append({
                    "Stock":          sym,
                    "Company":        names.get(sym, sym),
                    "Price (₹)":      round(price, 2),
                    "Mkt Cap (Cr)":   round(mc / 1e7),
                    "Above 200 EMA%": above_200_pct,
                    "Vol Ratio":      vol_ratio,
                    "Prior Uptrend":  "Yes" if prior_up      else "No",
                    "3D Squeeze":     "Yes" if squeeze3      else "No",
                    "Net Accum":      "Yes" if net_accum     else "No",
                    "Rising Lows":    "Yes" if rising_lows   else "No",
                    "Entry Trigger":  "Yes" if entry_trigger else "No",
                    "Score /10":      score,
                    "Buy Zone":       f"{buy_lo}-{buy_hi}",
                    "Target (₹)":    target,
                    "Stop (₹)":      stop,
                    "R:R":            rr,
                    "Chart":          f"https://www.tradingview.com/chart/?symbol=NSE:{sym}",
                })
        except Exception:
            pass

    _log(f"Scoring complete: {len(rows)} stocks qualify (score ≥ 5)")

    top = sorted(rows, key=lambda r: (r["Score /10"], r["Vol Ratio"]), reverse=True)[:15]
    _log("Top 15 picks:")
    for i, r in enumerate(top, 1):
        _log(f"  {i:2d}. {r['Stock']:12s}  Score {r['Score /10']}/10  Vol {r['Vol Ratio']:.1f}x  Price ₹{r['Price (₹)']}")

    # ── Step 6: Top 30 daily movers ───────────────────────────────────────────
    _save_daily_top(all_close, names)

    # ── Step 7 & 8: Bottom Formation + Consolidation scans ────────────────────
    bottom_rows = _scan_bottom(all_close, all_high, all_low, all_vol, names, mcap_data)
    consol_rows = _scan_consol(all_close, all_high, all_low, all_vol, names, mcap_data)

    # ── Step 9: Save all 3 results to one combined sheet in history.xlsx ──────
    _save_combined_history(rows, bottom_rows, consol_rows)

if __name__ == "__main__":
    try:
        run()
    except Exception as e:
        _log(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
