import json
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from server import connections, storage
from server.messages import FORMAT_ERROR, build_message, parse_client_message

app = FastAPI()

TEST_PAGE = Path(__file__).resolve().parent.parent / "client" / "test.html"


@app.get("/")
def root():
    return {"status": "server is reachable"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, last_id: int = 0):
    try:
        await connections.connect(websocket, last_id)
        while True:
            raw = await websocket.receive_text()  
            try:
                sender, text = parse_client_message(raw)
            except ValueError:
                await websocket.send_text(json.dumps({"error": FORMAT_ERROR}))
                continue
            async with connections.lock:
                message = build_message(sender, text)
                storage.save(message)
                await connections.send_to_all(message)
    except WebSocketDisconnect:
        pass
    finally:
        connections.disconnect(websocket)

@app.get("/test", response_class=HTMLResponse)
def test_page():
    return TEST_PAGE.read_text(encoding="utf-8")