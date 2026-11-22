import json
from datetime import datetime, timezone

FORMAT_ERROR = 'Expected JSON like {"sender": "name", "text": "message"}'

next_id = 1


def parse_client_message(raw: str) -> tuple[str, str]:
    """Check text received from a client and return (sender, text).

    Raises ValueError if it is not valid JSON, a field is missing,
    a field is not text, or a field is empty.
    """
    try:
        data = json.loads(raw)
        sender = data["sender"]
        text = data["text"]
    except (ValueError, KeyError, TypeError):
        raise ValueError("invalid message")
    if not isinstance(sender, str) or not isinstance(text, str):
        raise ValueError("sender and text must be text")
    if sender.strip() == "" or text.strip() == "":
        raise ValueError("sender and text must not be empty")
    return sender, text


def build_message(sender: str, text: str) -> dict:
    """Wrap sender and text in the full message format, adding id and time."""
    global next_id
    message = {
        "id": next_id,
        "sender": sender,
        "text": text,
        "time": datetime.now(timezone.utc).isoformat(),
    }
    next_id += 1
    return message
