import asyncio
import websockets
import json

async def send_test_data():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as ws:
        data = {
            "feeds": {
                "NSE_EQ|RELIANCE": {
                    "fullFeed": {
                        "marketFF": {
                            "ltpc": {
                                "ltp": 2798.75,
                                "open": 2750.00
                            },
                            "marketLevel": {},
                            "optionGreeks": {}
                        }
                    },
                    "requestMode": "full_d5"
                },
                "NSE_EQ|TCS": {
                    "fullFeed": {
                        "marketFF": {
                            "ltpc": {
                                "ltp": 3850.40,
                                "open": 3825.00
                            },
                            "marketLevel": {},
                            "optionGreeks": {}
                        }
                    },
                    "requestMode": "full_d5"
                }
            },
            "currentTs": "1752406018836"
        }
        await ws.send(json.dumps(data))

asyncio.run(send_test_data())
