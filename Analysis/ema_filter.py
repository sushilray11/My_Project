"""
EMA Filter — adds 200 EMA condition to fundamental screener results.
Reads: exports/fundamental_screener_20261004.xlsx (Filtered Stocks sheet)
Filter: current price is at most 20% above the 200-day EMA
Output: exports/fundamental_screener_ema_20261006.xlsx
"""

import datetime
import os
import time

INPUT_FILE  = "exports/fundamental_screener_20261004.xlsx"
OUTPUT_FILE = "exports/fundamental_screener_ema_20261006.xlsx"
EMA_PERIOD  = 200
MAX_PREMIUM = 0.20   # price must be <= EMA200 * (1 + 0.20)


def fetch_ema200_batch(symbols: list) -> dict:
    """Batch-fetch 1y price data and return {symbol: (current_price, ema200, pct_above)} dict."""
    import yfinance as yf
    import pandas as pd

    tickers = [f"{s}.NS" for s in symbols]
    print(f"Downloading price data for {len(tickers)} stocks (batch)...")
    raw = yf.download(tickers, period="1y", auto_adjust=True, progress=False)

    results = {}
    close = raw["Close"] if "Close" in raw else raw

    for sym in symbols:
        ticker = f"{sym}.NS"
        try:
            series = close[ticker].dropna()
            if len(series) < 50:
                results[sym] = None
                continue

            ema200     = series.ewm(span=EMA_PERIOD, adjust=False).mean().iloc[-1]
            curr_price = series.iloc[-1]
            pct_above  = (curr_price - ema200) / ema200 * 100

            results[sym] = {
                "current_price": round(float(curr_price), 2),
                "ema200":        round(float(ema200), 2),
                "pct_above_ema": round(float(pct_above), 2),
            }
        except Exception:
            results[sym] = None

    return results


def write_excel(filtered_df, all_df, output_path: str):
    from openpyxl import Workbook
    from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    import pandas as pd

    def thin():
        s = Side(style="thin", color="D1D5DB")
        return Border(left=s, right=s, top=s, bottom=s)

    def hdr(cell, value):
        cell.value     = value
        cell.fill      = PatternFill("solid", fgColor="1D4ED8")
        cell.font      = Font(color="FFFFFF", bold=True, size=10, name="Calibri")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border    = thin()

    def dat(cell, value, bg="FFFFFF", align="center", bold=False, color="1F2937"):
        cell.value     = value
        cell.fill      = PatternFill("solid", fgColor=bg)
        cell.font      = Font(color=color, bold=bold, size=10, name="Calibri")
        cell.alignment = Alignment(horizontal=align, vertical="center")
        cell.border    = thin()

    COLS = [
        "Symbol", "Company Name", "Sector",
        "Price (₹)", "EMA 200", "% Above EMA200",
        "PE Ratio",
        "Net Profit Y1 (Cr)", "Net Profit Y2 (Cr)", "Net Profit Y3 (Cr)",
        "Growth Y2→Y1 %", "Growth Y3→Y2 %",
        "Mkt Cap (Cr)",
    ]
    COL_WIDTHS = [10, 32, 22, 11, 11, 15, 10, 16, 16, 16, 14, 14, 14]

    wb = Workbook()
    wb.remove(wb.active)

    for sheet_name, df in [("Filtered (EMA Added)", filtered_df), ("All 128 With EMA", all_df)]:
        ws = wb.create_sheet(sheet_name)
        ws.freeze_panes = "A2"
        ws.row_dimensions[1].height = 36

        for ci, h in enumerate(COLS, 1):
            hdr(ws.cell(row=1, column=ci), h)
            ws.column_dimensions[get_column_letter(ci)].width = COL_WIDTHS[ci-1]

        for ri, row in enumerate(df.itertuples(index=False), 2):
            row_bg = "EFF6FF" if ri % 2 == 0 else "FFFFFF"
            pct    = getattr(row, "_5", None)   # % Above EMA200 column index

            vals = [
                row.Symbol,
                getattr(row, "Company_Name", ""),
                row.Sector,
                getattr(row, "Price___", None),
                getattr(row, "EMA_200", None),
                pct,
                getattr(row, "PE_Ratio", None),
                getattr(row, "Net_Profit_Y1__Cr_", None),
                getattr(row, "Net_Profit_Y2__Cr_", None),
                getattr(row, "Net_Profit_Y3__Cr_", None),
                getattr(row, "Growth_Y2_Y1__", None),
                getattr(row, "Growth_Y3_Y2__", None),
                getattr(row, "Mkt_Cap__Cr_", None),
            ]

            for ci, val in enumerate(vals, 1):
                cell  = ws.cell(row=ri, column=ci)
                align = "left" if ci in (1, 2, 3) else "center"

                if ci == 6 and isinstance(val, (int, float)):   # % Above EMA200
                    bg = "DCFCE7" if val <= 0 else ("FFF9C4" if val <= 10 else ("FFE0B2" if val <= 20 else "FEE2E2"))
                elif ci in (11, 12) and isinstance(val, (int, float)):  # Growth %
                    bg = "DCFCE7" if val > 0 else "FEE2E2"
                else:
                    bg = row_bg

                dat(cell, val, bg=bg, align=align)
                ws.row_dimensions[ri].height = 20

                if ci in (4, 5) and val is not None:
                    cell.number_format = "#,##0.00"
                elif ci == 6 and val is not None:
                    cell.number_format = "0.00"
                elif ci == 7 and val is not None:
                    cell.number_format = "0.0"
                elif ci in (8, 9, 10, 13) and val is not None:
                    cell.number_format = "#,##0.00"
                elif ci in (11, 12) and val is not None:
                    cell.number_format = "0.0"

    # Summary
    ws_sum = wb.create_sheet("Summary", 0)
    ws_sum.column_dimensions["A"].width = 36
    ws_sum.column_dimensions["B"].width = 16
    ws_sum.row_dimensions[1].height = 32
    hdr(ws_sum.cell(row=1, column=1), "Metric")
    hdr(ws_sum.cell(row=1, column=2), "Value")
    summary = [
        ("Run Date",                          datetime.date.today().strftime("%d-%b-%Y")),
        ("Input: Stocks (PE<40 + Profit↑)",   len(all_df)),
        ("EMA data not available",             int(all_df["EMA 200"].isna().sum())),
        ("Within 20% above EMA200",            len(filtered_df)),
        ("Removed (>20% above EMA200)",        len(all_df) - len(filtered_df)),
    ]
    for ri, (label, val) in enumerate(summary, 2):
        dat(ws_sum.cell(row=ri, column=1), label, align="left", bold=True)
        dat(ws_sum.cell(row=ri, column=2), val,   align="center")
        ws_sum.row_dimensions[ri].height = 22

    wb.save(output_path)


def main():
    import pandas as pd

    print("\n" + "="*60)
    print("  EMA Filter — adding 200 EMA condition to 128 stocks")
    print("  Condition: price ≤ EMA200 × 1.20  (max 20% above EMA)")
    print("="*60 + "\n")

    # Load existing filtered stocks
    df = pd.read_excel(INPUT_FILE, sheet_name="Filtered Stocks")
    symbols = df["Symbol"].tolist()
    print(f"Loaded {len(symbols)} stocks from {INPUT_FILE}\n")

    # Batch fetch EMA200 for all stocks at once
    ema_data = fetch_ema200_batch(symbols)

    # Attach EMA columns
    df["Price (₹)"]       = df["Symbol"].map(lambda s: ema_data.get(s, {}) and ema_data[s]["current_price"] if ema_data.get(s) else None)
    df["EMA 200"]          = df["Symbol"].map(lambda s: ema_data.get(s, {}) and ema_data[s]["ema200"]        if ema_data.get(s) else None)
    df["% Above EMA200"]   = df["Symbol"].map(lambda s: ema_data.get(s, {}) and ema_data[s]["pct_above_ema"] if ema_data.get(s) else None)

    # Fix boolean-typed values from the lambda (Python `and` returns the value, not bool)
    for col in ["Price (₹)", "EMA 200", "% Above EMA200"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Print per-stock result
    for _, row in df.iterrows():
        pct = row["% Above EMA200"]
        if pct is None or (isinstance(pct, float) and pct != pct):  # NaN check
            status = "✗ no price data"
        elif pct <= MAX_PREMIUM * 100:
            status = f"✓  {pct:+.1f}% above EMA200"
        else:
            status = f"✗  {pct:+.1f}% above EMA200 (too high)"
        print(f"  {row['Symbol']:<16} {status}")

    # Apply filter
    filtered = df[
        df["% Above EMA200"].notna() &
        (df["% Above EMA200"] <= MAX_PREMIUM * 100)
    ].copy()

    # Reorder columns — put EMA columns right after Symbol/Name/Sector
    orig_cols = [c for c in df.columns if c not in ["Price (₹)", "EMA 200", "% Above EMA200", "PE < 40", "Profit Growing"]]
    new_order = ["Symbol", "Company Name", "Sector", "Price (₹)", "EMA 200", "% Above EMA200"] + \
                [c for c in orig_cols if c not in ["Symbol", "Company Name", "Sector", "Price (₹)"]]
    df_out       = df.reindex(columns=[c for c in new_order if c in df.columns])
    filtered_out = filtered.reindex(columns=[c for c in new_order if c in filtered.columns])

    write_excel(filtered_out, df_out, OUTPUT_FILE)

    print(f"\n{'='*60}")
    print(f"  Input stocks        : {len(df)}")
    print(f"  Passed EMA filter   : {len(filtered)}")
    print(f"  Removed             : {len(df) - len(filtered)}")
    print(f"  Saved to: {OUTPUT_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
