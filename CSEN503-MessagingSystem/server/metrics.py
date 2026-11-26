import json
import time
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from server import connections, storage

router = APIRouter()

START_TIME = time.time()

WINDOW_SECONDS = 10


def collect_metrics() -> dict:
    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=WINDOW_SECONDS)

    recent_count = 0
    recent_bytes = 0
    for message in reversed(storage.messages):
        created = datetime.fromisoformat(message["time"])
        if created < window_start:
            break
        recent_count += 1
        recent_bytes += len(json.dumps(message).encode("utf-8"))

    return {
        "active_connections": len(connections.connected_clients),
        "total_messages": len(storage.messages),
        "window_seconds": WINDOW_SECONDS,
        "messages_per_second": round(recent_count / WINDOW_SECONDS, 2),
        "bytes_per_second": round(recent_bytes / WINDOW_SECONDS, 1),
        "uptime_seconds": int(time.time() - START_TIME),
    }


@router.get("/metrics")
def metrics_json():
    return collect_metrics()


METRICS_PAGE = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Server metrics</title>
<style>
  body { font-family: sans-serif; margin: 20px; }
  table { border-collapse: collapse; }
  td { padding: 6px 14px; border-bottom: 1px solid #ccc; }
  td.value { font-weight: bold; text-align: right; }
  #status { color: gray; margin-top: 10px; }
</style>
</head>
<body>
<h2>Server metrics</h2>
<table id="table"></table>
<div id="status">loading...</div>
<script>
const LABELS = {
  active_connections: "Active connections",
  total_messages: "Total messages",
  messages_per_second: "Messages / second",
  bytes_per_second: "Bytes / second",
  window_seconds: "Rate window (s)",
  uptime_seconds: "Uptime (s)"
};

async function refresh() {
  try {
    const response = await fetch("/metrics");
    const data = await response.json();
    let rows = "";
    for (const key in LABELS) {
      rows += "<tr><td>" + LABELS[key] + "</td><td class='value'>" + data[key] + "</td></tr>";
    }
    document.getElementById("table").innerHTML = rows;
    document.getElementById("status").textContent = "updated " + new Date().toLocaleTimeString();
  } catch (error) {
    document.getElementById("status").textContent = "server not reachable";
  }
}

refresh();
setInterval(refresh, 1000);
</script>
</body>
</html>"""


@router.get("/metrics/page", response_class=HTMLResponse)
def metrics_page():
    return METRICS_PAGE
