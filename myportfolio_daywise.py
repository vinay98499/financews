import streamlit as st
import pandas as pd
import json
import os
import time
from streamlit_autorefresh import st_autorefresh

# Auto refresh every 10 seconds
st_autorefresh(interval=10000, key="refresh")

st.set_page_config(page_title="Daily Loss Tracker", layout="wide")
st.title("📉 Real-Time Portfolio Daily Loss Tracker")

# -------- Load Portfolio --------
DEFAULT_FILE = "Stocks_Holdings_Statement_14-02-2026.xlsx"

@st.cache_data
def load_portfolio(file):
    df_raw = pd.read_excel(file, sheet_name=0)
    df = df_raw.iloc[10:].copy()
    df.columns = df_raw.iloc[9]
    df = df[1:]
    df = df.dropna(subset=["Stock Name"])
    df.reset_index(drop=True, inplace=True)

    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    return df

uploaded_file = st.sidebar.file_uploader("Upload Portfolio", type=["xlsx"])
portfolio_df = load_portfolio(uploaded_file) if uploaded_file else load_portfolio(DEFAULT_FILE)

# -------- Load Instrument Mapping --------
with open("instrument_map.json", "r") as f:
    INSTRUMENT_NAMES = json.load(f)

# Reverse mapping (Stock Name → Instrument Key)
NAME_TO_KEY = {v: k for k, v in INSTRUMENT_NAMES.items()}

# -------- Load Latest Feed --------
feed_path = os.path.join(os.path.dirname(__file__), "latest_feed.json")

def get_latest_feed():
    if os.path.exists(feed_path):
        with open(feed_path, "r") as f:
            try:
                return json.load(f), os.path.getmtime(feed_path)
            except:
                return None, None
    return None, None

feed, last_modified = get_latest_feed()

if not feed:
    st.warning("Waiting for live feed...")
    st.stop()

if last_modified:
    st.caption("Last updated: " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(last_modified)))

feeds = feed.get("feeds", {})

# -------- Extract Market Data --------
market_data = {}

for symbol, data in feeds.items():
    try:
        instrument_key = symbol.split("|")[1]
        name = INSTRUMENT_NAMES.get(instrument_key, instrument_key)

        marketFF = data["fullFeed"]["marketFF"]
        ltp = marketFF["ltpc"]["ltp"]

        ohlc_list = marketFF.get("marketOHLC", {}).get("ohlc", [])
        prev_close = None

        for entry in ohlc_list:
            if entry.get("interval") == "1d":
                prev_close = entry.get("close")
                break

        if prev_close is None and ohlc_list:
            prev_close = ohlc_list[0].get("close")

        market_data[name] = {
            "ltp": ltp,
            "prev_close": prev_close
        }

    except Exception as e:
        continue

# -------- Merge Portfolio + Market Data --------
rows = []

for _, row in portfolio_df.iterrows():
    stock_name = row["Stock Name"]
    qty = row["Quantity"]

    if stock_name in market_data:
        ltp = market_data[stock_name]["ltp"]
        prev_close = market_data[stock_name]["prev_close"]

        if prev_close and qty:
            day_pl = qty * (ltp - prev_close)
            day_pct = ((ltp - prev_close) / prev_close) * 100

            rows.append({
                "Stock": stock_name,
                "Qty": qty,
                "Prev Close": round(prev_close, 2),
                "Current": round(ltp, 2),
                "Day P/L ₹": round(day_pl, 2),
                "Day P/L %": round(day_pct, 2)
            })

result_df = pd.DataFrame(rows)

if result_df.empty:
    st.warning("No matching stocks found between portfolio and live feed.")
    st.stop()

# -------- Portfolio Metrics --------
total_day_pl = result_df["Day P/L ₹"].sum()

col1, col2 = st.columns(2)

col1.metric("📊 Total Daily P/L", f"₹{total_day_pl:,.2f}")
col2.metric("📉 Biggest Loss", 
            result_df.nsmallest(1, "Day P/L ₹")["Stock"].values[0])

# -------- Table --------
st.subheader("📋 Daily Profit / Loss per Stock")

result_df = result_df.sort_values("Day P/L ₹")

st.dataframe(result_df, use_container_width=True)

# -------- Top Losers --------
st.subheader("📉 Top 5 Daily Losers")

top_losers = result_df.nsmallest(5, "Day P/L ₹")
st.table(top_losers[["Stock", "Day P/L ₹", "Day P/L %"]])

# -------- Chart --------
st.subheader("📊 Daily P/L Distribution")
st.bar_chart(result_df.set_index("Stock")["Day P/L ₹"])
