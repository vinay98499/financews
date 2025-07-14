import streamlit as st
import asyncio
import websockets
import threading
import json
from streamlit_autorefresh import st_autorefresh

# Refresh UI every 3 seconds
st_autorefresh(interval=10000, key="auto-refresh")

# ---- Shared data + lock ----
latest_data = {}
data_lock = threading.Lock()
rowstemp = []
row3 = []
# ✅ FUNCTION: Store received data from WebSocket
def set_latest_data(data: dict):
    print("Setting latest data...",data)
    rows2 = []
    global latest_data
    with data_lock:
        latest_data.clear()
        latest_data.update(data)
        print("✅ Data stored via set_latest_data()")
        feeds = latest_data.get("feeds", {})
        print("Feeds--->:", feeds)  # Debugging output
        rows = []

        for symbol_key, feed_data in feeds.items():
            symbol = symbol_key.split("|")[1]
            ltpc = (
                feed_data.get("fullFeed", {})
                .get("marketFF", {})
                .get("ltpc", {})
            )
            ltp = ltpc.get("ltp", "--")
            open_price = ltpc.get("open", "--")

            rows.append({
                "Symbol": symbol,
                "Current Price": ltp,
                "Opening Price": open_price
            })
            print(f"Row added for {symbol}: {ltp}, {open_price}")
        rows2 = rows
        print("Rows prepared for display:row2", rows)    
    row3 = rows2 
    print("✅ Data set successfully row3",row3)
    st.info(row3)
    st.dataframe(row3, use_container_width=True)
    
print("Streamlit app started, waiting for WebSocket data...",row3)
print("Streamlit app started, waiting for WebSocket data...",latest_data)

st.info(row3)
st.dataframe(row3, use_container_width=True)
# ✅ FUNCTION: Get data safely for UI
def get_latest_data() -> dict:
    with data_lock:
        return latest_data.copy()

# ✅ WebSocket listener function
async def listen_to_websocket():
    uri = "ws://localhost:8000/ws"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                print("✅ Connected to WebSocket relay")
                while True:
                    msg = await websocket.recv()
                    try:
                        data = json.loads(msg)
                        print("📥 Received:", data)
                        set_latest_data(data)
                    except Exception as e:
                        print("❌ JSON decode error:", e)
        except Exception as e:
            print("⚠️ WebSocket error:", e)
            await asyncio.sleep(5)

# ✅ Start background thread once
if "ws_started" not in st.session_state:
    threading.Thread(target=lambda: asyncio.run(listen_to_websocket()), daemon=True).start()
    st.session_state.ws_started = True

# ==============================
# ✅ MAIN STREAMLIT UI BELOW
# ==============================

st.title("📈 Live Stock Feed from Relay Server")

# Get latest data
display_data = latest_data.copy()

# Debugging: Show raw JSON
st.subheader("📦 Raw Feed JSON")
st.json(display_data)


# for symbol_key, feed_data in feeds.items():
#     symbol = symbol_key.split("|")[1]
#     ltpc = (
#         feed_data.get("fullFeed", {})
#         .get("marketFF", {})
#         .get("ltpc", {})
#     )
#     ltp = ltpc.get("ltp", "--")
#     open_price = ltpc.get("open", "--")

#     rows.append({
#         "Symbol": symbol,
#         "Current Price": ltp,
#         "Opening Price": open_price
#     })


