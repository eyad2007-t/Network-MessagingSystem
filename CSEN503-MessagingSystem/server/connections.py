import asyncio
import json

from fastapi import WebSocket

from server import storage

connected_clients: list[WebSocket] = []

lock = asyncio.Lock()


async def connect(websocket: WebSocket, last_id: int = 0) -> None:
    await websocket.accept()
    async with lock:
        for message in storage.messages_after(last_id):
            await websocket.send_text(json.dumps(message))
        connected_clients.append(websocket)
    print(f"Client connected. Total: {len(connected_clients)}")


def disconnect(websocket: WebSocket) -> None:
    if websocket in connected_clients:
        connected_clients.remove(websocket)
    print(f"Client disconnected. Total: {len(connected_clients)}")


async def send_to_all(message: dict) -> None:
    data = json.dumps(message) 
    for client in list(connected_clients): 
        try:
            await client.send_text(data)
        except Exception:
            if client in connected_clients:
                connected_clients.remove(client)
            print(f"Removed a dead client. Total: {len(connected_clients)}")