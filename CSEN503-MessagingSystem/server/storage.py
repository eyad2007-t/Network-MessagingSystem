messages: list[dict] = []


def save(message: dict) -> None:
    messages.append(message)


def messages_after(last_id: int) -> list[dict]:
    return [message for message in messages if message["id"] > last_id]