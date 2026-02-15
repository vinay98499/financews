import streamlit as st
import json
import os
import time
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10000, key="auto-refresh")

st.set_page_config(page_title="Upstox Market Feed", layout="wide")
st.title("📊 Upstox Live Market Feed - Summary")

# Load instrument key-name mapping
with open('instrument_map.json', 'r') as f:
    INSTRUMENT_NAMES = json.load(f)

# Feed file path
feed_path = os.path.join(os.path.dirname(__file__), 'latest_feed.json')

def get_latest_feed():
    if os.path.exists(feed_path):
        with open(feed_path, 'r') as f:
            try:
                return json.load(f), os.path.getmtime(feed_path)
            except Exception:
                return None, None
    return None, None

feed, last_modified = get_latest_feed()

if feed:
    if last_modified:
        st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_modified))}")

    feeds = feed.get("feeds", {})
    all_rows = []

    for symbol, data in feeds.items():
        try:
            instrument_key = symbol.split("|")[1]
            name = INSTRUMENT_NAMES.get(instrument_key, instrument_key)
            indexFF = data["fullFeed"]["marketFF"]
            ltp = indexFF["ltpc"]["ltp"]

            ohlc_list = indexFF.get("marketOHLC", {}).get("ohlc", [])

            # Try to get 1d interval; if not, fallback to the first ohlc entry
            ohlc_data = next((entry for entry in ohlc_list if entry.get("interval") == "1d"), None)
            if not ohlc_data and ohlc_list:
                ohlc_data = ohlc_list[0]

            if ohlc_data:
                row = {
                    "Stock Name": name,
                    "Open": ohlc_data.get("open"),
                    "High": ohlc_data.get("high"),
                    "Low": ohlc_data.get("low"),
                    "LTP": ltp
                }
                all_rows.append(row)
            else:
                st.info(f"No OHLC data for: {name}")
        except Exception as e:
            st.warning(f"Failed to parse {symbol}: {e}")

    if all_rows:
        st.dataframe(all_rows, use_container_width=True)
    else:
        st.info("No stock data available to display.")
else:
    st.info("Waiting for live market feed...")
