from __future__ import annotations

import json
from datetime import datetime, timezone
from queue import Queue
from uuid import uuid4


class EventBus:
    def __init__(self, queue: Queue, session_id: str, request_id: str, version: str = "1.0"):
        self.queue = queue
        self.session_id = session_id
        self.request_id = request_id
        self.version = version
        self._seq = 0

    def emit(self, event_type: str, payload: dict, parent_event_id: str | None = None, trace_id: str | None = None):
        self._seq += 1
        envelope = {
            "version": self.version,
            "event_id": str(uuid4()),
            "seq": self._seq,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "request_id": self.request_id,
            "event_type": event_type,
            "payload": payload,
            "trace_id": trace_id,
            "parent_event_id": parent_event_id,
        }
        self.queue.put(envelope)
        return envelope


def to_sse(envelope: dict) -> str:
    return f"event: {envelope['event_type']}\ndata: {json.dumps(envelope, ensure_ascii=False)}\n\n"
