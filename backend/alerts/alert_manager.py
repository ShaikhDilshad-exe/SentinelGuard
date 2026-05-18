"""
Alert Manager Module
Manages alert generation, storage, and distribution.
"""

import uuid
import time
import threading
import logging
from collections import deque
from typing import Dict, List, Optional, Union
from enum import Enum

logger = logging.getLogger(__name__)

class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertManager:
    """Manage threat alerts and notifications with thread-safe in-memory storage"""
    
    def __init__(self, max_alerts: int = 1000):
        """Initialize alert manager"""
        # Upgraded to a bounded deque to prevent memory leaks from infinite alerts
        self.alerts = deque(maxlen=max_alerts)
        self.subscribers: List[callable] = []
        self._lock = threading.Lock() # Crucial for background thread safety
    
    def create_alert(
        self, 
        severity: Union[str, AlertSeverity], 
        message: str, 
        source: str, 
        threat_data: Optional[dict] = None
    ) -> dict:
        """
        Create a new alert in the standardized format.
        """
        sev_value = severity.value if isinstance(severity, AlertSeverity) else str(severity).lower()

        alert = {
            "id": str(uuid.uuid4()),        # Changed to UUID for unique React keys
            "type": source,                 # Standardized to "type"
            "severity": sev_value.upper(),
            "message": message,
            "timestamp": time.time(),
            "metadata": threat_data or {},
            "resolved": False
        }
        
        # Thread-safe storage
        with self._lock:
            self.alerts.appendleft(alert) # Add to front so newest are first
            
        self._notify_subscribers(alert)
        logger.info(f"Alert created: {alert['id']} - Type: {source} - Severity: {sev_value.upper()}")
        return alert
    
    def get_all_alerts(self) -> List[Dict[str, any]]:
        """
        Retrieves all alerts, sorted with the most recent first.
        """
        return sorted(self.alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def get_alerts(self, limit: int = 100, severity: str = None) -> List[dict]:
        """
        Retrieve alerts with optional filtering
        """
        with self._lock:
            alerts_list = list(self.alerts)
            
        if severity:
            alerts_list = [a for a in alerts_list if a["severity"] == severity.upper()]
        return alerts_list[:limit]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        with self._lock:
            for alert in self.alerts:
                if alert["id"] == alert_id:
                    alert["resolved"] = True
                    logger.info(f"Alert {alert_id} marked as resolved")
                    return True
        return False
    
    def subscribe(self, callback: callable) -> None:
        """Subscribe to alert notifications"""
        with self._lock:
            self.subscribers.append(callback)
    
    def _notify_subscribers(self, alert: dict) -> None:
        """Notify all subscribers of new alert"""
        # Copy subscribers safely to avoid lock issues during external callbacks
        with self._lock:
            subs = list(self.subscribers)
            
        for subscriber in subs:
            try:
                subscriber(alert)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")