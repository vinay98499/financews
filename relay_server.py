import asyncio
import websockets
import json

clients = set()

async def relay(websocket):
    clients.add(websocket)
    try:
        async for message in websocket:
            # Broadcast to all clients except sender
            for client in clients:
                if client != websocket:
                    await client.send(message)
    finally:
        clients.remove(websocket)

if __name__ == "__main__":
    async def main():
        async with websockets.serve(relay, "localhost", 8000):
            print("Relay WebSocket server started on ws://localhost:8000")
            await asyncio.Future()  # run forever
    asyncio.run(main())
