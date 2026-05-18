"""
Centralized Event Collector
Aggregates and normalizes data from all system monitors into a standard format.
"""

import time
import logging
import threading
from collections import deque
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class EventCollector:
    """
    In-memory queue for centralized event normalization and storage.
    Thread-safe for use across multiple background monitoring threads.
    """
    
    def __init__(self, max_size: int = 5000):
        self.events = deque(maxlen=max_size)
        self._lock = threading.Lock()

    def add_event(self, event_type: str, metadata: Dict[str, Any]) -> None:
        if event_type not in ("process", "file", "network"):
            logger.warning(f"EventCollector: Unrecognized event type '{event_type}'")

        normalized_event = {
            "type": event_type,
            "timestamp": time.time(),
            "metadata": metadata
        }

        with self._lock:
            self.events.append(normalized_event)

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self.events)[-limit:]

    def get_all_events(self) -> List[Dict[str, Any]]:
        """
        Returns a copy of all current events, sorted with the most recent first.
        """
        with self._lock:
            # Return a copy to avoid race conditions if the list is read while being modified
            return sorted(list(self.events), key=lambda x: x.get('timestamp', 0), reverse=True)

    def flush_events(self) -> List[Dict[str, Any]]:
        with self._lock:
            current_events = list(self.events)
            self.events.clear()
            return current_events