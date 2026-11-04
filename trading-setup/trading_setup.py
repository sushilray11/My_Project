"""
Simple Short-Term Trading Setup
================================
Strategy: EMA Crossover + RSI Confirmation
Timeframe: 15-min charts (yfinance real data)
Asset: Any liquid stock or crypto

ENTRY RULES
-----------
Long  (BUY):
  1. EMA 9 crosses ABOVE EMA 21
  2. RSI > 50
  3. Volume >= 1.2x 20-bar average

Short (SELL):
  1. EMA 9 crosses BELOW EMA 21
  2. RSI < 50
  3. Volume >= 1.2x 20-bar average

EXIT RULES
----------
  - Stop Loss : 1.5% against entry
  - Take Profit: 3.0% in your favor (2:1 R/R)
  - Force Exit : EMA crossover reversal
"""

import sys
import warnings
import pandas as pd
import numpy as np
import yfinance as yf

warnings.filterwarnings("ignore")


# ── Indicators ────────────────────────────────────────────────────────────────

def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


# ── Data Fetching ─────────────────────────────────────────────────────────────

def fetch_data(ticker: str, interval: str = "15m", period: str = "60d") -> pd.DataFrame:
    """
    Fetch real OHLCV data from Yahoo Finance.
    interval: 1m, 5m, 15m, 1h, 1d
    period:   7d, 60d, 6mo, 1y  (intraday limited to 60d max)
    """
    raw = yf.download(ticker, interval=interval, period=period,
                      auto_adjust=True, progress=False)
    if raw.empty:
        raise ValueError(f"No data returned for {ticker!r}. Check ticker symbol.")

    # yfinance may return MultiIndex columns — flatten them
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = [col[0].lower() for col in raw.columns]
    else:
        raw.columns = [c.lower() for c in raw.columns]

    df = raw[["open", "high", "low", "close", "volume"]].dropna()
    print(f"  Fetched {len(df)} bars for {ticker} ({interval}, {period})")
    return df


# ── Signal Generation ─────────────────────────────────────────────────────────

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["ema9"]    = ema(df["close"], 9)
    df["ema21"]   = ema(df["close"], 21)
    df["rsi"]     = rsi(df["close"], 14)
    df["avg_vol"] = df["volume"].rolling(20).mean()

    prev9  = df["ema9"].shift(1)
    prev21 = df["ema21"].shift(1)

    bullish_cross = (prev9 <= prev21) & (df["ema9"] > df["ema21"])
    bearish_cross = (prev9 >= prev21) & (df["ema9"] < df["ema21"])
    vol_ok        = df["volume"] >= df["avg_vol"] * 1.2

    df["signal"] = 0
    df.loc[bullish_cross & (df["rsi"] > 50) & vol_ok, "signal"] =  1
    df.loc[bearish_cross & (df["rsi"] < 50) & vol_ok, "signal"] = -1
    return df


# ── Backtester ────────────────────────────────────────────────────────────────

def backtest(df: pd.DataFrame, stop_pct: float = 0.015, target_pct: float = 0.03):
    signals  = generate_signals(df)
    trades   = []
    position = None

    for idx, (ts, row) in enumerate(signals.iterrows()):
        if position is not None:
            side  = position["side"]
            entry = position["entry"]
            sl    = entry * (1 - side * stop_pct)
            tp    = entry * (1 + side * target_pct)
            price = float(row["close"])

            hit_sl   = (side ==  1 and price <= sl) or (side == -1 and price >= sl)
            hit_tp   = (side ==  1 and price >= tp) or (side == -1 and price <= tp)
            reversal = (side ==  1 and row["ema9"] < row["ema21"]) or \
                       (side == -1 and row["ema9"] > row["ema21"])

            if hit_tp or hit_sl or reversal:
                exit_price = tp if hit_tp else (sl if hit_sl else price)
                pnl_pct    = side * (exit_price - entry) / entry * 100
                reason     = "TP" if hit_tp else ("SL" if hit_sl else "REVERSAL")
                trades.append({
                    "entry_time": position["entry_time"],
                    "exit_time" : ts,
                    "side"      : "LONG" if side == 1 else "SHORT",
                    "entry"     : round(entry, 4),
                    "exit"      : round(exit_price, 4),
                    "pnl_%"     : round(pnl_pct, 3),
                    "reason"    : reason,
                })
                position = None

        if position is None and row["signal"] != 0:
            position = {
                "side"      : int(row["signal"]),
                "entry"     : float(row["close"]),
                "entry_time": ts,
            }

    if not trades:
        return trades, {"total_trades": 0}

    results = pd.DataFrame(trades)
    wins    = results[results["pnl_%"] > 0]
    losses  = results[results["pnl_%"] <= 0]

    summary = {
        "total_trades": len(results),
        "wins"        : len(wins),
        "losses"      : len(losses),
        "win_rate_%"  : round(len(wins) / len(results) * 100, 1),
        "avg_win_%"   : round(wins["pnl_%"].mean(), 3)   if len(wins)   else 0,
        "avg_loss_%"  : round(losses["pnl_%"].mean(), 3) if len(losses) else 0,
        "total_pnl_%" : round(results["pnl_%"].sum(), 3),
    }
    return trades, summary


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    ticker   = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    interval = sys.argv[2] if len(sys.argv) > 2 else "15m"
    period   = sys.argv[3] if len(sys.argv) > 3 else "60d"

    print(f"\n=== TRADING SETUP: EMA9/21 + RSI + Volume  |  {ticker} {interval} ===\n")
    print("Entry Rules:")
    print("  LONG  → EMA9 crosses above EMA21, RSI > 50, Volume ≥ 1.2x avg")
    print("  SHORT → EMA9 crosses below EMA21, RSI < 50, Volume ≥ 1.2x avg")
    print("\nExit Rules:")
    print("  Stop Loss  : 1.5%  |  Take Profit: 3.0%  |  Force: EMA reversal\n")

    df = fetch_data(ticker, interval=interval, period=period)
    trades, summary = backtest(df)

    print("\n=== BACKTEST RESULTS ===\n")
    if summary["total_trades"] == 0:
        print("  No trades found. Try a different ticker or timeframe.")
    else:
        for k, v in summary.items():
            print(f"  {k:<18} {v}")

        print("\n--- All Trades ---")
        for t in trades:
            print(f"  {t['side']:<5}  {str(t['entry_time'])[:16]}  "
                  f"entry={t['entry']:.2f}  exit={t['exit']:.2f}  "
                  f"pnl={t['pnl_%']:+.2f}%  [{t['reason']}]")
