# Import necessary modules
import asyncio
import json
import ssl
import upstox_client
import websockets
from google.protobuf.json_format import MessageToDict
import os
import MarketDataFeed_pb2 as pb
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),  '..')))

from utils import SecretsUtil

access_token = SecretsUtil.get_token()

def get_market_data_feed_authorize(api_version, configuration):
    """Get authorization for market data feed."""
    api_instance = upstox_client.WebsocketApi(
        upstox_client.ApiClient(configuration))
    api_response = api_instance.get_market_data_feed_authorize(api_version)
    return api_response


def decode_protobuf(buffer):
    """Decode protobuf message."""
    feed_response = pb.FeedResponse()
    feed_response.ParseFromString(buffer)
    return feed_response


async def fetch_market_data():
    """Fetch market data using WebSocket and print it."""

    # Create default SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Configure OAuth2 access token for authorization
    configuration = upstox_client.Configuration()

    api_version = '2.0'
    configuration.access_token = access_token

    # Get market data feed authorization
    response = get_market_data_feed_authorize(
        api_version, configuration)

    # Connect to the WebSocket with SSL context
    async with websockets.connect(response.data.authorized_redirect_uri, ssl=ssl_context) as websocket:
        print('Connection established')
        await asyncio.sleep(1)  # Wait for 1 second

        # Data to be sent over the WebSocket
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": [
                    "NSE_EQ|RELIANCE", "NSE_EQ|TCS", "NSE_EQ|HDFCBANK", "NSE_EQ|INFY", "NSE_EQ|ICICIBANK",
                    "NSE_EQ|LT", "NSE_EQ|ITC", "NSE_EQ|KOTAKBANK", "NSE_EQ|SBIN", "NSE_EQ|BHARTIARTL",
                    "NSE_EQ|HINDUNILVR", "NSE_EQ|AXISBANK", "NSE_EQ|BAJFINANCE", "NSE_EQ|ASIANPAINT", "NSE_EQ|HCLTECH",
                    "NSE_EQ|MARUTI", "NSE_EQ|SUNPHARMA", "NSE_EQ|TITAN", "NSE_EQ|ULTRACEMCO", "NSE_EQ|BAJAJFINSV",
                    "NSE_EQ|WIPRO", "NSE_EQ|POWERGRID", "NSE_EQ|ONGC", "NSE_EQ|TATAMOTORS", "NSE_EQ|NTPC",
                    "NSE_EQ|JSWSTEEL", "NSE_EQ|ADANIPORTS", "NSE_EQ|DIVISLAB", "NSE_EQ|GRASIM", "NSE_EQ|TATASTEEL",
                    "NSE_EQ|CIPLA", "NSE_EQ|BPCL", "NSE_EQ|TECHM", "NSE_EQ|HDFCLIFE", "NSE_EQ|BRITANNIA",
                    "NSE_EQ|EICHERMOT", "NSE_EQ|SHREECEM", "NSE_EQ|HEROMOTOCO", "NSE_EQ|COALINDIA", "NSE_EQ|BAJAJ-AUTO",
                    "NSE_EQ|INDUSINDBK", "NSE_EQ|APOLLOHOSP", "NSE_EQ|DRREDDY", "NSE_EQ|SBILIFE", "NSE_EQ|M&M",
                    "NSE_EQ|TATACONSUM", "NSE_EQ|HINDALCO", "NSE_EQ|UPL", "NSE_EQ|ADANIENT", "NSE_EQ|SRF"
                ]
            }
        }

        # Send subscription as text (not binary)
        await websocket.send(json.dumps(data))

        # Open relay server connection
        async with websockets.connect('ws://localhost:8000') as relay_ws:
            print('Connected to relay server')
            # Continuously receive and decode data from WebSocket
            while True:
                try:
                    message = await websocket.recv()
                    decoded_data = decode_protobuf(message)
                    data_dict = MessageToDict(decoded_data)

                    # Extract and print LTP for all Nifty 50 stocks if present
                    feeds = data_dict.get("feeds", {})
                    ltp_dict = {}
                    for symbol, stock_data in feeds.items():
                        try:
                            ltp = stock_data["fullFeed"]["marketFF"]["ltpc"]["ltp"] \
                                if "marketFF" in stock_data["fullFeed"] else stock_data["fullFeed"]["indexFF"]["ltpc"]["ltp"]
                            ltp_dict[symbol] = ltp
                            print(f"{symbol} LTP: {ltp}")
                        except Exception:
                            pass
                    # Forward LTPs to relay server as JSON
                    if ltp_dict:
                        await relay_ws.send(json.dumps(ltp_dict))
                except Exception as e:
                    print(f"Error: {e}")
                    break

async def fetch_market_data2():
    """Fetch market data using WebSocket and print it."""

    # Create default SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Configure OAuth2 access token for authorization
    configuration = upstox_client.Configuration()
    api_version = '2.0'
    configuration.access_token = access_token

    # Get market data feed authorization
    response = get_market_data_feed_authorize(api_version, configuration)

    # Connect to the WebSocket with SSL context
    async with websockets.connect(response.data.authorized_redirect_uri, ssl=ssl_context) as websocket:
        print('Connection established')
        await asyncio.sleep(1)  # Wait for 1 second

        # Data to be sent over the WebSocket
        data = {
            "guid": "someguid",
            "method": "sub",
            "data": {
                "mode": "full",
                "instrumentKeys": [
                    "NSE_EQ|RELIANCE", "NSE_EQ|TCS", "NSE_EQ|HDFCBANK", "NSE_EQ|INFY", "NSE_EQ|ICICIBANK",
                    "NSE_EQ|LT", "NSE_EQ|ITC", "NSE_EQ|KOTAKBANK", "NSE_EQ|SBIN", "NSE_EQ|BHARTIARTL",
                    "NSE_EQ|HINDUNILVR", "NSE_EQ|AXISBANK", "NSE_EQ|BAJFINANCE", "NSE_EQ|ASIANPAINT", "NSE_EQ|HCLTECH",
                    "NSE_EQ|MARUTI", "NSE_EQ|SUNPHARMA", "NSE_EQ|TITAN", "NSE_EQ|ULTRACEMCO", "NSE_EQ|BAJAJFINSV",
                    "NSE_EQ|WIPRO", "NSE_EQ|POWERGRID", "NSE_EQ|ONGC", "NSE_EQ|TATAMOTORS", "NSE_EQ|NTPC",
                    "NSE_EQ|JSWSTEEL", "NSE_EQ|ADANIPORTS", "NSE_EQ|DIVISLAB", "NSE_EQ|GRASIM", "NSE_EQ|TATASTEEL",
                    "NSE_EQ|CIPLA", "NSE_EQ|BPCL", "NSE_EQ|TECHM", "NSE_EQ|HDFCLIFE", "NSE_EQ|BRITANNIA",
                    "NSE_EQ|EICHERMOT", "NSE_EQ|SHREECEM", "NSE_EQ|HEROMOTOCO", "NSE_EQ|COALINDIA", "NSE_EQ|BAJAJ-AUTO",
                    "NSE_EQ|INDUSINDBK", "NSE_EQ|APOLLOHOSP", "NSE_EQ|DRREDDY", "NSE_EQ|SBILIFE", "NSE_EQ|M&M",
                    "NSE_EQ|TATACONSUM", "NSE_EQ|HINDALCO", "NSE_EQ|UPL", "NSE_EQ|ADANIENT", "NSE_EQ|SRF"
                ]
            }
        }

        # Send subscription as text (not binary)
        await websocket.send(json.dumps(data))

        print("Subscription sent. Waiting for data...")

        # Print every raw message received from Upstox
        while True:
            try:
                message = await websocket.recv()
                print("Raw message received from Upstox:", message)
            except Exception as e:
                print(f"Error receiving data: {e}")
                break


# Execute the function to fetch market data
asyncio.run(fetch_market_data2())

