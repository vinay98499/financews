# Import necessary modules
import asyncio
import json
import ssl
import websockets
import requests
from google.protobuf.json_format import MessageToDict
import MarketDataFeedV3_pb2 as pb
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from utils import SecretsUtil

access_token = SecretsUtil.get_token()

def get_market_data_feed_authorize_v3():
    """Get authorization for market data feed."""
    print("Using UPSTOX_ACCESS_TOKEN from secrets.json:", access_token)
    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    url = 'https://api.upstox.com/v3/feed/market-data-feed/authorize'
    api_response = requests.get(url=url, headers=headers)
    return api_response.json()


def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response


async def fetch_market_data():
    """Fetch market data using WebSocket and print it."""
    import websockets as ws_client
    relay_uri = "ws://localhost:8000/ws"
    relay_ws = None
    try:
        relay_ws = await ws_client.connect(relay_uri)
        print(f"Connected to relay server at {relay_uri}")
    except Exception as e:
        print(f"Could not connect to relay server: {e}")
        relay_ws = None

    # Create default SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Get market data feed authorization
    response = get_market_data_feed_authorize_v3()
    print("Authorization API response:", response)
    if not response or "data" not in response:
        print("Error: No 'data' in response. Check your access token and API credentials.")
        return
    # Connect to the WebSocket with SSL context
    async with websockets.connect(response["data"]["authorized_redirect_uri"], ssl=ssl_context) as websocket:
        print('Connection established')

        await asyncio.sleep(1)  # Wait for 1 second

        # Data to be sent over the WebSocket
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": [ "NSE_EQ|RELIANCE", "NSE_EQ|TCS", "NSE_EQ|HDFCBANK", "NSE_EQ|INFY", "NSE_EQ|ICICIBANK",
                    "NSE_EQ|LT", "NSE_EQ|ITC", "NSE_EQ|KOTAKBANK", "NSE_EQ|SBIN", "NSE_EQ|BHARTIARTL",
                    "NSE_EQ|HINDUNILVR", "NSE_EQ|AXISBANK", "NSE_EQ|BAJFINANCE", "NSE_EQ|ASIANPAINT", "NSE_EQ|HCLTECH",
                    "NSE_EQ|MARUTI", "NSE_EQ|SUNPHARMA", "NSE_EQ|TITAN", "NSE_EQ|ULTRACEMCO", "NSE_EQ|BAJAJFINSV",
                    "NSE_EQ|WIPRO", "NSE_EQ|POWERGRID", "NSE_EQ|ONGC", "NSE_EQ|TATAMOTORS", "NSE_EQ|NTPC",
                    "NSE_EQ|JSWSTEEL", "NSE_EQ|ADANIPORTS", "NSE_EQ|DIVISLAB", "NSE_EQ|GRASIM", "NSE_EQ|TATASTEEL",
                    "NSE_EQ|CIPLA", "NSE_EQ|BPCL", "NSE_EQ|TECHM", "NSE_EQ|HDFCLIFE", "NSE_EQ|BRITANNIA",
                    "NSE_EQ|EICHERMOT", "NSE_EQ|SHREECEM", "NSE_EQ|HEROMOTOCO", "NSE_EQ|COALINDIA", "NSE_EQ|BAJAJ-AUTO",
                    "NSE_EQ|INDUSINDBK", "NSE_EQ|APOLLOHOSP", "NSE_EQ|DRREDDY", "NSE_EQ|SBILIFE", "NSE_EQ|M&M",
                    "NSE_EQ|TATACONSUM", "NSE_EQ|HINDALCO", "NSE_EQ|UPL", "NSE_EQ|ADANIENT", "NSE_EQ|SRF"]
            }
        }

        # Convert data to binary and send over WebSocket
        binary_data = json.dumps(data).encode('utf-8')
        await websocket.send(binary_data)

        # Continuously receive and decode data from WebSocket
        while True:
            message = await websocket.recv()
            decoded_data = decode_protobuf(message)
            # Convert the decoded data to a dictionary
            data_dict = MessageToDict(decoded_data)

            # Send to relay server if connected
            if relay_ws:
                print("Sending data to relay server...")
                try:
                    await relay_ws.send(json.dumps(data_dict))
                except Exception as e:
                    print(f"Relay send error: {e}")
            # Save the latest data_dict to a file for Streamlit UI
            with open(os.path.join(os.path.dirname(__file__), '../../latest_feed.json'), 'w') as f:
                json.dump(data_dict, f)

            # Print the dictionary representation
            print(json.dumps(data_dict))


# Execute the function to fetch market data
asyncio.run(fetch_market_data())
