import streamlit as st
import json
import os
import time
import json

# Load mapping
with open('instrument_map.json', 'r') as f:
    INSTRUMENT_NAMES = json.load(f)

from streamlit_autorefresh import st_autorefresh

# Refresh UI every 3 seconds
st_autorefresh(interval=10000, key="auto-refresh")

st.set_page_config(page_title="Upstox Live Market Feed", layout="wide")
st.title("📈 Upstox Live Market Feed")

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
    # st.write("**Raw Feed Data:**")
    # st.json(feed)
    if last_modified:
        st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_modified))}")

    feeds = feed.get("feeds", {})
    for symbol, data in feeds.items():
        instrumentKey = symbol.split("|")[1];                
        name = INSTRUMENT_NAMES.get(instrumentKey, instrumentKey)
        st.subheader(f"{name} ({instrumentKey})")
        try:   
            indexFF = data["fullFeed"]["marketFF"]
            ltp = indexFF["ltpc"]["ltp"]
            st.metric("LTP", ltp)
            ohlc_list = indexFF["marketOHLC"]["ohlc"]
            st.write("OHLC Data")
            st.table(ohlc_list)
        except Exception as e:
            st.warning(f"Could not parse feed for {symbol}: {e}")
else:
    st.info("Waiting for live market feed...")

