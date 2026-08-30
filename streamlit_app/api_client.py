import json
from collections.abc import Iterator
from typing import Any

import httpx


def iter_stream_chat(
    api_base: str,
    session_id: str,
    user_query: str,
) -> Iterator[dict[str, Any]]:
    """Stream SSE packets from POST /stream-chat until stream.end."""
    base = api_base.rstrip("/")
    payload = {"session_id": session_id, "user_query": user_query}

    with httpx.Client(timeout=None) as client:
        with client.stream("POST", f"{base}/stream-chat", json=payload) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line.startswith("data: "):
                    continue
                packet = json.loads(line[6:])
                yield packet
                if packet.get("event") == "stream.end":
                    break
