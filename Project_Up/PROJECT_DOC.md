# Project_Up — Documentation

## What It Does
Screens all NSE-listed equity stocks daily to find the **top 20 setups most likely to move up in 1–7 trading days**, using a Price-Volume Action (PVA) scoring model. Results are shown in a Streamlit dashboard and saved to Excel for tracking and backtesting.

---

## Files Overview

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard — Screener tab + Backtest tab |
| `daily_run.py` | Headless screener — same logic, no UI, for cron/automation |
| `history.xlsx` | Cumulative log of screener picks (top 20 per date) |
| `backtest_results.xlsx` | Backtest output — forward returns for all history picks |
| `universe_cache.json` | NSE equity universe cache (refreshed weekly) |
| `mcap_cache.json` | Market-cap cache per stock (refreshed weekly) |

---

## Screener Pipeline (5 Steps)

### Step 1 — Universe
- Downloads full NSE equity list from `archives.nseindia.com/content/equities/EQUITY_L.csv`
- Cached in `universe_cache.json` for 7 days to avoid repeated fetches
- ~2,000–2,200 NSE symbols

### Step 2 — Price Data Download
- Downloads 1-year OHLCV history via `yfinance` in batches of 400 stocks
- Stores Close, High, Low, Volume, Open per stock
- Skips stocks with < 60 days of data

### Step 3 — 200 EMA Filter (Hard Filter)
- Keeps only stocks where **current price > 200-period EMA**
- Ensures only stocks in a long-term uptrend are considered
- Typically passes ~40–60% of universe

### Step 4 — Market Cap Filter (Hard Filter)
- Keeps only stocks with **market cap ≥ ₹100 Cr** (10 billion)
- Mcap fetched via `yfinance.Ticker.fast_info.market_cap`
- Cached in `mcap_cache.json` for 7 days

### Step 5 — PVA Scoring (10 Signals)
Each signal scores 1 point. Minimum **5/10 to appear** in results.

| # | Signal | Condition |
|---|---|---|
| 1 | **Vol Dry-Up** | Today's volume < 70% of 20-day avg |
| 2 | **Vol Lowest 5D** | Today's volume = lowest in last 5 days |
| 3 | **3D Squeeze** | 3-day price range < 4% of price (tight consolidation) |
| 4 | **Prior Uptrend** | Price today > price 16 days ago |
| 5 | **Net Accumulation** | Up-day volume > 1.2× down-day volume over last 10 days |
| 6 | **Weak Selling** | No down-day in last 5 days had volume ≥ 80% of avg |
| 7 | **Rising Lows** | Lows: L[-1] > L[-4] > L[-7] (higher lows pattern) |
| 8 | **Bullish Closes** | Last 3 days avg close position in range ≥ 55% |
| 9 | **At Support** | Price within ±2% of EMA20 or ±1% of EMA50 |
| 10 | **Entry Trigger** | Today: volume up AND price up vs yesterday |

**Score ≥ 8 = High Conviction** setup.

### Trade Parameters (for qualifying stocks)
- **Buy Zone:** ±0.5% of current price
- **Stop Loss:** 5-day low × 0.99
- **Target:** lower of (price × 1.07) or (52-week high × 0.995)
- **R:R:** reward / risk ratio

---

## Excel Files — When & What Updates

### `history.xlsx`

**Updated by:** Clicking "🚀 Find Top Upside Setups" in the dashboard, OR running `daily_run.py`

**What it stores:** Top 20 qualifying stocks per trading day

**Columns:** Date, Stock, Company, Price (₹), Mkt Cap (Cr), Above 200 EMA%, Vol Ratio, Prior Uptrend, 3D Squeeze, Net Accum, Rising Lows, Entry Trigger, Score /10, Buy Zone, Target (₹), Stop (₹), R:R, Chart

**Rules:**
- Only saves on weekdays (Mon–Fri) — weekend runs use the last Friday's date
- Re-running on the same date **replaces** that date's rows (idempotent)
- Running on a new date **appends** new rows — old dates are preserved
- Top 20 sorted by: Score → Vol Ratio → Mkt Cap

---

### `backtest_results.xlsx`

**Updated by:** Clicking "📊 Run Backtest" in the Backtest tab

**What it stores:** Forward return performance of every pick in history.xlsx

**Sheets:**
- **Pick Results** — one row per pick per date with columns: Date, Stock, Company, Score, Pick ₹, D+1 ₹, D+3 ₹, D+5 ₹, D+1 %, D+3 %, D+5 %
- **Summary** — hit-rate and avg return stats for "All Picks", "Score ≥ 8", "Score 5–7"

**How returns are calculated:**
- Reads last 10 unique pick-dates from `history.xlsx`
- Downloads 3-month price history for each stock via yfinance
- Finds the pick date's position in the trading-day price series (last trading day ≤ pick date, to handle weekend-dated picks)
- D+1/D+3/D+5 = price at 1/3/5 **trading days** after the pick (not calendar days)
- Shows "Pending" if fewer than 5 trading days have passed since the pick

**Rules:**
- Currently **overwrites** the file on each run (does not accumulate)
- Returns are "N/A" if price data is unavailable for that stock

---

## `backtest.py` — Standalone Headless Backtest

A command-line script that runs the same backtest as the UI tab, but without Streamlit. Useful for running via cron or terminal after `daily_run.py`.

**Run it:**
```
python3 /Users/I325211/Local_Project/Project_Up/backtest.py
```

**What it does:**
1. Reads `history.xlsx` — takes the last 10 unique pick-dates
2. Downloads 3-month price history for all picked stocks via yfinance
3. For each pick, finds the pick price at the last trading day ≤ pick date (handles weekend-dated picks)
4. Calculates D+1 / D+3 / D+5 forward returns (trading days, not calendar days)
5. Prints a summary table to console (hit rate + avg return for All Picks, Score ≥ 8, Score 5–7)
6. Saves `backtest_results.xlsx` with two sheets:
   - **Pick Results** — Date, Stock, Company, Score, Pick ₹, D+1 ₹/%, D+3 ₹/%, D+5 ₹/%, ✅/❌ per horizon
   - **Summary** — hit-rate and avg return grouped by All / Score ≥ 8 / Score 5–7

**Key logic:**
- Returns marked `—` if forward date hasn't arrived yet (pending)
- Skips stocks with no price data in the downloaded batch
- Overwrites `backtest_results.xlsx` on every run (does not accumulate)
- Exits with code 0 (no error) if history.xlsx has no forward data yet

**Difference vs UI Backtest tab:**
| | `backtest.py` | Backtest tab in `app.py` |
|---|---|---|
| Requires Streamlit | No | Yes |
| Output | Console + Excel | Dashboard + Excel |
| Suitable for cron | Yes | No |
| Logic | Identical | Identical |

---

## Automation (`daily_run.py`)

Headless version — identical screener logic, no Streamlit. Run via cron:

```
0 15 * * 1-5 python3 /Users/I325211/Local_Project/Project_Up/daily_run.py >> /Users/I325211/Local_Project/Project_Up/daily_run.log 2>&1
```

- Runs at 3:00 PM Mon–Fri (after NSE market close at 3:30 PM IST — adjust time if needed)
- Appends timestamped logs to `daily_run.log`
- Saves top 20 picks to `history.xlsx` using the same weekend-safe date logic
- Does NOT update `backtest_results.xlsx` — that is UI-only

---

## Weekend / Holiday Behaviour

| Scenario | Behaviour |
|---|---|
| Run screener on Saturday/Sunday | Date saved as the preceding Friday |
| Run screener on a market holiday | Date saved as-is (no holiday calendar — Friday rule only) |
| Pick date in history.xlsx is a weekend | Backtest uses the Friday price as the pick price |
| Run `daily_run.py` on weekend | Saves to history.xlsx with Friday's date |
