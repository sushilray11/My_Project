# Analysis Project — Documentation

## What It Does
Screens the **NSE F&O stock universe** (~200 stocks) daily across three distinct strategies to find actionable trade setups. Results are shown in a Streamlit dashboard, saved to history Excel, and backtested against forward returns.

---

## Files Overview

| File | Purpose |
|---|---|
| `app.py` | Streamlit dashboard — 5 sections (3 screeners, backtest, F&O list) |
| `daily_export.py` | Headless daily export — runs all 3 screeners, saves to dated Excel + history |
| `backtest.py` | Standalone headless backtest — reads history, calculates returns, saves Excel |
| `exports/screener_YYYY-MM-DD.xlsx` | Dated screener output (one file per trading day) |
| `exports/consolidated_history.xlsx` | Cumulative history — wide format, one sheet per screener |
| `exports/backtest_results.xlsx` | Backtest results — pick-by-pick returns, growing over time |
| `fno_cache.json` | F&O symbols cache (refreshed periodically) |

---

## Universe
- Only **NSE F&O listed stocks** (~200 stocks) — not the full NSE equity universe
- Symbol list fetched from NSE and cached in `fno_cache.json`
- All three screeners run over the same F&O universe

---

## Section 1 — Probable Upside (Next 1–2 Weeks)

**Goal:** Find F&O stocks already in an uptrend that are pausing/consolidating and ready to resume upward.

### Hard Filters (must pass to be scored)
| Filter | Condition |
|---|---|
| Above SMA200 | Current price > 200-day SMA |
| Not Overbought | RSI < 80 |

### 10 Setup Signals (Score /10)
| # | Signal | Condition |
|---|---|---|
| 1 | **Golden Alignment** | SMA20 > SMA50 |
| 2 | **Full Trend** | SMA50 > SMA200 |
| 3 | **SMA20 Rising** | Last 5D avg close > prior 5D avg close |
| 4 | **MACD Positive** | EMA12 > EMA26 |
| 5 | **RSI Healthy Zone** | RSI between 45–72 |
| 6 | **Net Accumulation** | Up-day volume > 1.2× down-day volume (last 10D) |
| 7 | **Vol Dry-Up** | Today's volume < 70% of 20D avg |
| 8 | **At Support** | Price within ±2% of EMA20 or ±1% of EMA50 |
| 9 | **Rising Lows** | Low[-1] > Low[-4] > Low[-7] |
| 10 | **Entry Trigger** | Volume up AND price closed up today vs yesterday |

**Minimum score to appear:** 7/10  
**Quality tiers:** Prime = 10/10 · Sweet Spot = 8–9/10 · Strong = 7/10  
**Sort order:** Prime first → Score (desc) → Vol Ratio (desc)  
**Display:** Top 20

---

## Section 2 — Support Entry Screener

**Goal:** Find F&O stocks sitting at a key support level, forming a base, ready to bounce.

### Hard Filters
| Filter | Condition |
|---|---|
| Above SMA200 | Price > 200-day SMA |
| Near Support | Gap to nearest support = 0–4% |
| Healthy Pullback | Pulled back 3–25% from 20D high |

### Support Sources (used to find nearest support)
- Swing lows (last 60 bars — local minima)
- SMA20, SMA50, SMA200

Nearest support = closest level at or below current price.

### 10 Base Formation Signals (Score /10)
| # | Signal | Condition |
|---|---|---|
| 1 | **Close to Support** | Gap to nearest support ≤ 1.5% |
| 2 | **Prior Uptrend** | SMA50 now ≥ SMA50 from 20 days ago |
| 3 | **Confluence** | 2+ support sources within 1.5% of nearest support |
| 4 | **Proven Support** | Nearest support tested ≥ 2 times in last 120 bars |
| 5 | **Base Forming** | 5D price range (High–Low) < 5% of price |
| 6 | **Vol Condition** | Declining vol (5D avg < 10D avg) OR surge (vol > 1.5× avg with up close) |
| 7 | **RSI Reset** | RSI between 35–65 (cooled, not oversold, not extended) |
| 8 | **Lows Stable** | Close[-1] ≥ Close[-5] (no new closing lows) |
| 9 | **Reversal Candle** | Lower wick at support OR 2-day consecutive up close |
| 10 | **Entry Trigger** | Vol up + close up today OR breaking above 5D base top with vol ≥ 80% avg |

**Minimum score to appear:** 5/10  
**High conviction:** Score ≥ 8  
**Trade parameters:**
- **Buy Zone:** Nearest support ±1% (0.99× to 1.02× support)
- **Stop Loss:** Nearest support × 0.97 (3% below support)
- **Target:** Higher of (60D swing high) or (price × 1.08)
- **Support type shown:** SMA 200 / SMA 50 / SMA 20 / Swing Low

---

## Section 3 — Consolidation Breakout Screener

**Goal:** Find F&O stocks coiling in a tight range above SMA50, ready to break out.

### Hard Filters
| Filter | Condition |
|---|---|
| 10D Range Tight | Last 10D range < 5% of price |
| Above SMA50 | Price > 50-day SMA |

### 10 Consolidation Signals (Score /10)
| # | Signal | Condition |
|---|---|---|
| 1 | **Very Tight Range** | 10D range < 3.5% (extra credit) |
| 2 | **Range Contracting** | 10D range < 50% of 30D range |
| 3 | **BB Squeeze** | Current Bollinger Band width < 80% of width 15 days ago |
| 4 | **Near Range High** | Price ≥ 95% of 20D high (consolidating at top) |
| 5 | **Vol Dry-Up** | 5D avg volume < 85% of 20D avg |
| 6 | **SMA20 Flat** | SMA20 moved < 1.2% in last 5D (sideways) |
| 7 | **Above SMA20** | Price > SMA20 |
| 8 | **Above SMA200** | Price > SMA200 (long-term uptrend) |
| 9 | **Prior Uptrend** | SMA50 now ≥ SMA50 from 20 days ago |
| 10 | **RSI Coiled** | RSI between 45–68 |

**Minimum score to appear:** 6/10  
**High conviction:** Score ≥ 8  
**Sort order:** Score (desc) → Days Consolidating (desc) → Range % (asc)  
**Trade parameters:**
- **Breakout Level:** Consolidation-period high × 1.005 (+0.5% above range)
- **Target:** Breakout level + (consolidation high − consolidation low) — measured move
- **Stop Loss:** Consolidation-period low × 0.98

---

## Section 4 — Backtest

**Goal:** Measure how each screener's picks actually performed at D+1/D+3/D+5.

**Data source:** `exports/consolidated_history.xlsx` — last 7 unique trading dates per screener sheet  
**Filters available in UI:** By screener · By date · By stock (text search)

**How returns are calculated:**
1. Reads wide-format history — dates as columns, stocks as rows
2. Skips weekend/holiday dates automatically
3. Downloads 3-month price data for all picked stocks
4. Finds pick price = last trading day ≤ pick date (handles any stale dates)
5. D+1/D+3/D+5 = price at 1/3/5 **trading days** after pick (not calendar days)
6. Shows `—` if forward date hasn't arrived yet

**Backtest Excel — append behaviour:**
- Loads existing `backtest_results.xlsx` (Pick Results sheet)
- Drops rows whose dates match current run (prevents duplicates)
- Appends new rows — historical dates from prior runs are preserved
- Rebuilds Summary sheet from full combined dataset each time

---

## Section 5 — NSE F&O Stocks

- Lists all F&O stocks with company name and TradingView chart link
- Optional: Load today's prices (current price + day % change)
- Searchable by symbol or company name

---

## Excel Files — When & What Updates

### `exports/consolidated_history.xlsx`

**Updated by:** Running `daily_export.py`  
**Format:** Wide format — dates as column headers, stocks listed under each date column  
**Sheets:** Probable Upside · Support Entry · Consolidation Breakout  
**Rules:**
- Only saves on weekdays — weekend runs exit immediately without writing anything
- `today_str` uses last trading day (Friday walk-back if run on weekend)
- Each run adds a new date column to each sheet
- Top 20 picks per screener per date

---

### `exports/screener_YYYY-MM-DD.xlsx`

**Updated by:** Running `daily_export.py`  
**Format:** One file per trading day — contains all 3 screener results as separate sheets  
**Rules:**
- Only created on weekdays — script exits at startup on Saturday/Sunday
- File name uses today's date — never overwritten after creation

---

### `exports/backtest_results.xlsx`

**Updated by:** Clicking "📊 Run Backtest" in the dashboard OR running `backtest.py`  
**Sheets:**
- **Pick Results** — Screener, Date, Stock, Pick ₹, D+1 %, D+3 %, D+5 %, ✅/❌ per horizon
- **Summary** — Hit rate + avg return for All Picks and each screener

**Rules:**
- **Accumulates over time** — new dates appended, same dates refreshed
- Old dates beyond the last 7 are preserved from previous runs
- Summary stats reflect the full all-time dataset, not just the latest run

---

## `backtest.py` — Standalone Headless Backtest

Run without opening the dashboard:
```
python3 /Users/I325211/Local_Project/Analysis/backtest.py
```

- Reads `consolidated_history.xlsx` — last 7 weekday dates, all 3 screeners
- Downloads 3-month price history for all picked stocks
- Calculates D+1/D+3/D+5 returns (same logic as UI)
- Prints hit-rate summary per screener to console
- Appends new dates to `backtest_results.xlsx` (same accumulate logic as UI)

---

## `daily_export.py` — Headless Daily Export

Run via cron or terminal after market close:
```
0 15 * * 1-5 cd /Users/I325211/Local_Project/Analysis && python3 daily_export.py >> exports/export_log.txt 2>&1
```

- Runs at 3:00 PM Mon–Fri
- Exits immediately on weekends — no files created
- Saves `screener_YYYY-MM-DD.xlsx` and updates `consolidated_history.xlsx`
- Does NOT update `backtest_results.xlsx` — that is backtest.py or UI-only

---

## Weekend / Holiday Behaviour

| Scenario | Behaviour |
|---|---|
| Run `daily_export.py` on Saturday/Sunday | Exits immediately — no files created, no history updated |
| Run `backtest.py` on weekend | Runs normally — skips weekend dates in history automatically |
| Run dashboard on weekend | Screeners work normally; backtest skips weekend dates |
| Pick date in history is a weekend | Backtest uses closest prior Friday's price as pick price |
| Market holiday (weekday) | No holiday calendar — script runs and saves as normal |
