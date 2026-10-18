"""
Fundamental Screener — Profit Growth + PE < 40
Fetches PE ratio and yearly net profit for NSE stocks via yfinance.
Filters: PE < 40 AND net profit increasing for at least 2 consecutive years.
Output: exports/fundamental_screener_YYYYMMDD.xlsx
Run: python3 fundamental_screener.py
Expected time: ~10-15 minutes for 350+ stocks.
"""

import time
import datetime
import os

STOCKS = [
    "SBC", "VENUSREM", "BLIGVS", "LAURUSLABS", "FRONTSP", "SIGMAADV", "SYRMA",
    "RAYMOND", "KPL", "UNIVASTU", "FCL", "E2E", "AEGISLOG", "AEROFLEX", "AVALON",
    "RADICO", "RRKABEL", "PAISALO", "OMNI", "CUPID", "FILATEX", "UNIMECH",
    "MODISONLTD", "NINSYS", "SHILPAMED", "DEEPINDS", "YATHARTH", "RAMRAT",
    "RATNAVEER", "ACMESOLAR", "PGIL", "MMP", "GANDHAR", "VENUSPIPES", "INDOBORAX",
    "FREDUN", "SHIRAS", "MBAPL", "KRN", "OCCLLTD", "DIVGIITTS", "DIACABS",
    "SHUKRAPHAR", "SBCL", "ONEPOINT", "AVL", "AXISCADES", "ASIANENE", "FINCABLES",
    "SYNCOMF", "AZAD", "PREMIERPOL", "SANSERA", "ABDL", "NEOGEN", "IOLCP",
    "SEDEMAC", "SAILIFE", "RBLBANK", "SANGHVIMOV", "GNA", "STALLION", "KIRLOSENG",
    "TDPOWERSYS", "MANORAMA", "BRPL", "SUNFLAG", "CEMPRO", "JGCHEM", "PLAZACABLE",
    "INNOVACAP", "SUVEN", "SOTL", "SUDEEPPHRM", "ATLANTAELE", "MARINE", "KRISHANA",
    "ASTRAMICRO", "CAPLIPOINT", "KROSS", "RPEL", "QPOWER", "RATEGAIN", "YASHO",
    "RML", "DIFFNKG", "MACPOWER", "ASKAUTOLTD", "VISHNU", "JAYKAY", "TEGA",
    "SCHNEIDER", "RACLGEAR", "PAR", "PAYTM", "LODHA", "PARAGMILK", "DEEDEV",
    "BELRISE", "PRECWIRE", "GHVINFRA", "AGI", "VISL", "JASH", "ACE", "CENTUM",
    "VMART", "ARTEMISMED", "INDOMIM", "ADVAIT", "MANINDS", "SUDARSCHEM", "CORDELIA",
    "KRONOX", "ALUFLUOR", "GANESHBE", "MITSU", "KISSHT", "MANALIPETC", "CEIGALL",
    "SOMANYCERA", "POWERICA", "EBGNG", "ADOR", "ALICON", "ATHERENERG", "JNKINDIA",
    "SGFIN", "PRITIKAUTO", "TORNTPHARM", "TI", "TALBROAUTO", "EMUDHRA", "AEQUS",
    "VIMTALABS", "GOKULAGRO", "ROSSTECH", "PITTIENG", "RUBICON", "THEJO", "SMLMAH",
    "SEJALLTD", "SUNDRMFAST", "SENORES", "GOODLUCK", "CGCL", "VIDHIING", "MINDACORP",
    "TAALTECH", "APCOTEXIND", "SIGNPOST", "PRASOLCHEM", "JAYBARMARU", "CHEMCON",
    "ABCAPITAL", "IIFLCAPS", "MENONBE", "UNIVCABLES", "PRIVISCL", "SUPRIYA",
    "EMMVEE", "PARADEEP", "BALAMINES", "SKIPPER", "SHADOWFAX", "SAKAR", "INDOCO",
    "DYCL", "CYIENTDLM", "DLTNCBL", "ENTERO", "GVPIL", "EMIL", "BALUFORGE",
    "AKUMS", "GEE", "LOTUSDEV", "TEMBO", "MILKYMIST", "EPACKPEB", "NITINSPIN",
    "MAYURUNIQ", "MANBA", "HBLENGINE", "WPIL", "SHAILY", "MGEL", "TIMETECHNO",
    "ONWARDTEC", "ALKALI", "CPPLUS", "GGAUTO", "SHYAMMETL", "SAGILITY", "BANSALWIRE",
    "TATVA", "RAJRATAN", "ZFSTEERING", "HAPPYFORGE", "GREAVESCOT", "MUFIN", "ZENTEC",
    "POCL", "NIBE", "NOVELIX", "RITESHIN", "ADFFOODS", "GMBREW", "CHOICEIN",
    "SONACOMS", "BEPL", "MPSLTD", "RELTD", "KSHINTL", "TINNARUBR", "PDSL",
    "SOLARA", "RPGLIFE", "AETHER", "ARCHIDPLY", "SGMART", "SHARDAMOTR", "EMCURE",
    "SAATVIKGL", "IDEAFORGE", "ACUTAAS", "POLYPLEX", "UNICHEMLAB", "ANANTRAJ",
    "PURPLEFIN", "NGLFINE", "JYOCNC", "AVTNPL", "FAIRCHEMOR", "FINEORG", "VIDYAWIRES",
    "RAIN", "PARAS", "CLEAN", "GOACARBON", "NGIL", "AMAL", "V2RETAIL", "PRIMO",
    "BLEL", "CMPDI", "HSCL", "HIGHENE", "GESHIP", "AARTISURF", "EIEL", "KMEW",
    "KSB", "KUSUMGAR", "AUROLAB", "ALKYLAMINE", "FORTIS", "DAAWAT", "BAJAJCON",
    "EXPLEOSOL", "VARROC", "TRUALT", "NSE", "BLUESTONE", "KIMS", "SETL",
    "PAUSHAKLTD", "PCBL", "MCCHRLS-B", "POWERMECH", "AJANTPHARM", "HEROMOTOCO",
    "BBOX", "ENDURANCE", "SANGAMIND", "RKFORGE", "ISGEC", "UNIPARTS", "NOCIL",
    "DHOOTTRANS", "JAGSNPHARM", "GPTHEALTH", "HONASA", "CGPOWER", "STYLAMIND",
    "AVANTEL", "A1L", "DEEPAKFERT", "EQUITASBNK", "SHRIPISTON", "PRICOLLTD",
    "SHALPAINTS", "SIKA", "GTV", "HMAAGRO", "TARIL", "GVT&D", "SENCO", "CMRGREEN",
    "THERMAX", "LXCHEM", "ARVSMART", "GALAXYSURF", "NAUKRI", "PINELABS", "OXYGENTAPH",
    "CORONA", "CARRARO", "INDOAMIN", "GUJTHEM", "ROTO", "TECHNOE", "THOMASCOTT",
    "AARTIIND", "CENTENKA", "MOTHERSON", "KIRLPNU", "TIPSMUSIC", "SANDHAR",
    "LASERPOWER", "PARKHOSPS", "INTERARCH", "ASTEC", "SFL", "GUJALKALI", "NDRAUTO",
    "GABRIEL", "EXICOM", "NELCAST", "PYRAMID", "INDIGOPNTS", "SHRJAGP", "XTGLOBAL",
    "BHARATSE", "AFIL", "IGARASHI", "SUREST", "SHAKTIPUMP", "VINATIORGA", "GOPAL",
    "TITANBIO", "SIGACHI", "DATAMATICS", "ATULAUTO", "LORDSCHLO", "GAEL", "KEI",
    "LUMINO", "KERNEX", "VGUARD", "DIAMONDYD", "KFINTECH", "DCMSRIND", "TRANSRAILL",
    "BLUECLOUDS", "VAML", "ANUHPHR", "GREENLAM", "SHIPROCKET", "KNACK", "THYROCARE",
    "MBEL", "NMDC", "NESCO", "CPL", "PRINCEPIPE", "PACEDIGITK", "AVANTIFEED",
    "BLUEJET", "EMSLIMITED", "HIKAL", "FABTECH", "AARON", "DPWIRES", "BALKRISIND",
    "SUNDRMBRAK", "CAMS", "PGEL", "ALLDIGI", "IFBAGRO", "MARSONS", "ASTERDM",
    "EPIGRAL", "MAXHEALTH", "REFEX", "TATACOMM", "SBIFUNDS", "ORIENTTECH", "BETA",
    "GKENERGY", "RAINBOW", "GODAVARIB", "BAJAJHCARE", "CONCOR", "COHANCE",
    "WALCHANNAG", "ERIS", "BAJEL", "MAPMYINDIA", "VIKRAN", "SPARC", "SWIGGY",
    "ROSSARI", "GULPOLY", "POPVEH", "IPL", "NAVKARCORP", "ELECON", "MODINSULAT",
    "OSWALPUMPS", "CIEINDIA", "GLOBUSSPR", "TTML", "CEWATER", "GOLDIAM", "CRSTCHM",
    "DCXINDIA", "VISTARAMAR", "VINYLINDIA", "WAAREERTL", "PSPPROJECT", "DSSL",
    "GRAVITA", "SCODATUBES", "AURIONPRO", "ORIBEVER", "BIGBLOC", "BHARATRAS",
    "CAMLINFINE", "MEIL", "WEL", "INOXGREEN", "DANUBE", "HGINFRA", "SWSOLAR",
    "WAAREEENER", "SHARDACROP", "PPAP", "SERVOTECH", "SKMEGGPROD", "INDIAGLYCO",
    "PAVNAIND", "NACLIND", "RMC", "KALIND",
]

PE_LIMIT      = 40
SLEEP_BETWEEN = 0.4   # seconds between each ticker to avoid rate limiting


def fetch_fundamentals(symbol: str):
    import yfinance as yf

    ticker_sym = f"{symbol}.NS"
    try:
        tkr  = yf.Ticker(ticker_sym)
        info = tkr.info

        # Skip if no meaningful data returned (yfinance returns a near-empty dict for unknown symbols)
        if not info or info.get("regularMarketPrice") is None and info.get("currentPrice") is None:
            return None

        pe     = info.get("trailingPE")
        price  = info.get("currentPrice") or info.get("regularMarketPrice")
        mcap   = info.get("marketCap")
        name   = info.get("longName") or info.get("shortName") or symbol
        sector = info.get("sector", "N/A")

        # Annual income statement — columns are dates (newest first)
        stmt = tkr.income_stmt
        if stmt is None or stmt.empty:
            return None

        net_income_row = None
        for idx in stmt.index:
            if "Net Income" in str(idx):
                net_income_row = stmt.loc[idx]
                break

        if net_income_row is None or len(net_income_row) < 3:
            return None

        # Values in INR; convert to Crores (÷ 1e7)
        values = [v for v in net_income_row.values if v is not None]
        if len(values) < 3:
            return None

        y1 = float(values[0]) / 1e7   # most recent year
        y2 = float(values[1]) / 1e7
        y3 = float(values[2]) / 1e7
        y4 = float(values[3]) / 1e7 if len(values) >= 4 else None

        g1 = round((y1 - y2) / abs(y2) * 100, 1) if y2 != 0 else None
        g2 = round((y2 - y3) / abs(y3) * 100, 1) if y3 != 0 else None

        return {
            "symbol":  symbol,
            "name":    name,
            "sector":  sector,
            "price":   round(price, 2) if price else None,
            "pe":      round(pe, 1)    if pe    else None,
            "mcap_cr": round(mcap / 1e7, 1) if mcap else None,
            "y1": round(y1, 2),
            "y2": round(y2, 2),
            "y3": round(y3, 2),
            "y4": round(y4, 2) if y4 is not None else None,
            "g1": g1,   # Y2→Y1 growth %
            "g2": g2,   # Y3→Y2 growth %
        }

    except Exception:
        return None


def passes_filters(d: dict):
    """Returns (pe_pass, profit_pass)."""
    pe_pass = d["pe"] is not None and d["pe"] < PE_LIMIT

    # Profit growing: Y1 > Y2 > Y3, all positive
    profit_pass = (
        d["y1"] is not None and d["y2"] is not None and d["y3"] is not None
        and d["y1"] > 0 and d["y2"] > 0 and d["y3"] > 0
        and d["y1"] > d["y2"] > d["y3"]
    )
    return pe_pass, profit_pass


def write_excel(filtered: list, all_results: list, not_found: list, path: str):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side

    def thin_border():
        s = Side(style="thin", color="D1D5DB")
        return Border(left=s, right=s, top=s, bottom=s)

    def hdr_cell(cell, value):
        cell.value = value
        cell.fill      = PatternFill("solid", fgColor="1D4ED8")
        cell.font      = Font(color="FFFFFF", bold=True, size=10, name="Calibri")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = thin_border()

    def data_cell(cell, value, bg="FFFFFF", bold=False, align="center", color="1F2937"):
        cell.value     = value
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.font      = Font(color=color, bold=bold, size=10, name="Calibri")
        cell.alignment = Alignment(horizontal=align, vertical="center")
        cell.border    = thin_border()

    HEADERS = [
        "Symbol", "Company Name", "Sector", "Price (₹)", "PE Ratio",
        "Net Profit Y1 (Cr)", "Net Profit Y2 (Cr)", "Net Profit Y3 (Cr)", "Net Profit Y4 (Cr)",
        "Growth Y2→Y1 %", "Growth Y3→Y2 %", "Mkt Cap (Cr)",
        "PE < 40", "Profit Growing",
    ]

    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, rows in [("Filtered Stocks", filtered), ("All Screened", all_results)]:
        ws = wb.create_sheet(sheet_name)
        ws.freeze_panes = "A2"
        ws.row_dimensions[1].height = 36

        for ci, h in enumerate(HEADERS, 1):
            hdr_cell(ws.cell(row=1, column=ci), h)

        for ri, d in enumerate(rows, 2):
            pe_pass, profit_pass = passes_filters(d)
            row_bg = "EFF6FF" if ri % 2 == 0 else "FFFFFF"

            vals = [
                d["symbol"], d["name"], d["sector"],
                d["price"], d["pe"],
                d["y1"], d["y2"], d["y3"], d["y4"],
                d["g1"], d["g2"], d["mcap_cr"],
                "✅" if pe_pass else "❌",
                "✅" if profit_pass else "❌",
            ]

            for ci, val in enumerate(vals, 1):
                cell = ws.cell(row=ri, column=ci)
                align = "left" if ci in (1, 2, 3) else "center"

                # Growth % — green/red tint
                if ci in (10, 11) and isinstance(val, (int, float)):
                    bg = "DCFCE7" if val > 0 else "FEE2E2"
                # Pass/fail columns
                elif ci == 13:
                    bg = "DCFCE7" if val == "✅" else "FEE2E2"
                elif ci == 14:
                    bg = "DCFCE7" if val == "✅" else "FEE2E2"
                else:
                    bg = row_bg

                data_cell(cell, val, bg=bg, align=align)
                ws.row_dimensions[ri].height = 20

                # Number formats
                if ci == 4 and val is not None:
                    cell.number_format = "#,##0.00"
                elif ci == 5 and val is not None:
                    cell.number_format = "0.0"
                elif ci in (6, 7, 8, 9, 12) and val is not None:
                    cell.number_format = "#,##0.00"
                elif ci in (10, 11) and val is not None:
                    cell.number_format = "0.0"

        # Auto-fit columns
        col_widths = [10, 32, 22, 11, 10, 16, 16, 16, 16, 14, 14, 14, 10, 14]
        for ci, w in enumerate(col_widths, 1):
            from openpyxl.utils import get_column_letter
            ws.column_dimensions[get_column_letter(ci)].width = w

    # Not Found sheet
    if not_found:
        ws3 = wb.create_sheet("Not Found")
        hdr_cell(ws3.cell(row=1, column=1), "Symbol")
        hdr_cell(ws3.cell(row=1, column=2), "Reason")
        ws3.column_dimensions["A"].width = 16
        ws3.column_dimensions["B"].width = 40
        for ri, sym in enumerate(not_found, 2):
            data_cell(ws3.cell(row=ri, column=1), sym, align="left")
            data_cell(ws3.cell(row=ri, column=2), "No data on Yahoo Finance / NSE", align="left")
            ws3.row_dimensions[ri].height = 20

    # Summary sheet
    ws_sum = wb.create_sheet("Summary", 0)
    ws_sum.column_dimensions["A"].width = 30
    ws_sum.column_dimensions["B"].width = 16
    summary_rows = [
        ("Run Date", datetime.date.today().strftime("%d-%b-%Y")),
        ("Total Stocks Checked", len(STOCKS)),
        ("Data Fetched", len(all_results)),
        ("Not Found / No Data", len(not_found)),
        ("PE < 40 (passed)", sum(1 for d in all_results if passes_filters(d)[0])),
        ("Profit Growing (passed)", sum(1 for d in all_results if passes_filters(d)[1])),
        ("Both Filters Passed", len(filtered)),
    ]
    hdr_cell(ws_sum.cell(row=1, column=1), "Metric")
    hdr_cell(ws_sum.cell(row=1, column=2), "Value")
    for ri, (label, val) in enumerate(summary_rows, 2):
        data_cell(ws_sum.cell(row=ri, column=1), label, align="left", bold=True)
        data_cell(ws_sum.cell(row=ri, column=2), val, align="center")
        ws_sum.row_dimensions[ri].height = 22
    ws_sum.row_dimensions[1].height = 32

    wb.save(path)


def main():
    total      = len(STOCKS)
    all_data   = []
    not_found  = []

    print(f"\n{'='*60}")
    print(f"  Fundamental Screener — {total} stocks")
    print(f"  Filters: PE < {PE_LIMIT}  |  Profit growing 2 consecutive years")
    print(f"  Est. time: {total * (SLEEP_BETWEEN + 1.5) / 60:.0f}–{total * (SLEEP_BETWEEN + 2.5) / 60:.0f} minutes")
    print(f"{'='*60}\n")

    for i, sym in enumerate(STOCKS, 1):
        print(f"[{i:>3}/{total}] Fetching {sym:<16}", end="", flush=True)
        result = fetch_fundamentals(sym)

        if result is None:
            not_found.append(sym)
            print("  ✗ no data")
        else:
            pe_pass, profit_pass = passes_filters(result)
            all_data.append(result)
            status = []
            if pe_pass:     status.append(f"PE={result['pe']}")
            if profit_pass: status.append("profit↑")
            print(f"  {'✓' if (pe_pass and profit_pass) else '·'}  {' | '.join(status) if status else ''}")

        time.sleep(SLEEP_BETWEEN)

    filtered = [d for d in all_data if all(passes_filters(d))]

    # Save Excel
    os.makedirs("exports", exist_ok=True)
    date_str  = datetime.date.today().strftime("%Y%m%d")
    out_path  = os.path.join("exports", f"fundamental_screener_{date_str}.xlsx")
    write_excel(filtered, all_data, not_found, out_path)

    print(f"\n{'='*60}")
    print(f"  Done.")
    print(f"  Stocks fetched   : {len(all_data)}")
    print(f"  Not found        : {len(not_found)}")
    print(f"  Passed both filters: {len(filtered)}")
    print(f"  Saved to: {out_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
