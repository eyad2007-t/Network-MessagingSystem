import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "chat.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False)

db.execute(
    """CREATE TABLE IF NOT EXISTS messages (
           id     INTEGER PRIMARY KEY,
           sender TEXT NOT NULL,
           text   TEXT NOT NULL,
           time   TEXT NOT NULL
       )"""
)
db.commit()

messages: list[dict] = [
    {"id": row[0], "sender": row[1], "text": row[2], "time": row[3]}
    for row in db.execute("SELECT id, sender, text, time FROM messages ORDER BY id")
]


def last_id() -> int:
    return messages[-1]["id"] if messages else 0


def save(message: dict) -> None:
    db.execute(
        "INSERT INTO messages (id, sender, text, time) VALUES (?, ?, ?, ?)",
        (message["id"], message["sender"], message["text"], message["time"]),
    )
    db.commit()
    messages.append(message)


def messages_after(last_id: int) -> list[dict]:
    return [message for message in messages if message["id"] > last_id]
