import asyncio
import websockets
import json

clients = set()

async def relay(websocket):
    clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"Received from client: {message}")
            # Broadcast to all clients (including sender)
            for client in clients:
                await client.send(message)
    finally:
        clients.remove(websocket)
        print(f"Client disconnected: {websocket.remote_address}")

if __name__ == "__main__":
    async def main():
        async with websockets.serve(relay, "localhost", 8000):
            print("Relay WebSocket server started on ws://localhost:8000")
            await asyncio.Future()  # run forever
    asyncio.run(main())
