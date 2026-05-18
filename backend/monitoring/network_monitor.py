"""
Network Monitor Module
Captures outgoing network connections and logs destination IP, port, and frequency.
"""

import time
import logging
import threading
import psutil
from collections import defaultdict
from backend.alerts.alert_manager import (
    AlertManager,
    AlertSeverity
)
from typing import List, Dict

logger = logging.getLogger(__name__)

class NetworkMonitor:
    """Monitors active network connections and tracks frequency."""
    
    def __init__(self, alert_manager: AlertManager, check_interval: int = 5):
        self.alert_manager = alert_manager
        self.check_interval = check_interval
        self.is_running = False
        self.monitor_thread = None
        self.event_collector = None
        self.known_conns = set()
        self.connection_frequency = defaultdict(int)
        self.standard_ports = {80, 443, 22, 21, 25, 110, 143, 993, 995}

    def _monitor_loop(self):
        """Background loop to periodically scan connections."""
        while self.is_running:
            self._scan_connections()
            time.sleep(self.check_interval)

    def _scan_connections(self):
        """Scans the system for established outgoing connections."""
        try:
            # kind='inet' filters for IPv4 and IPv6 connections
            connections = psutil.net_connections(kind='inet')
            
            for conn in connections:
                # We only care about established outgoing connections with a remote address
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    remote_ip = conn.raddr.ip
                    remote_port = conn.raddr.port
                    
                    # Ignore local loopback connections to reduce noise
                    if remote_ip in ('127.0.0.1', '::1', '0.0.0.0'):
                        continue
                        
                    # Update frequency count
                    conn_key = (remote_ip, remote_port)
                    self.connection_frequency[conn_key] += 1

                    # SEND RAW DATA TO THE CENTRAL EVENT COLLECTOR
                    if hasattr(self, 'event_collector') and self.event_collector:
                        self.event_collector.add_event(
                            event_type="network",
                            metadata={
                                "destination_ip": remote_ip,
                                "port": remote_port,
                                "pid": conn.pid,
                                "status": "ESTABLISHED"
                            }
                        )
                    
                    # Log unusual activity: First time connecting to a non-standard port
                    if remote_port not in self.standard_ports and self.connection_frequency[conn_key] == 1:
                        self.alert_manager.create_alert(
                            severity=AlertSeverity.LOW,
                            message=f"Connection to non-standard port: {remote_ip}:{remote_port}",
                            source="NetworkMonitor",
                            threat_data={
                                "destination_ip": remote_ip,
                                "port": remote_port,
                                "pid": conn.pid,
                                "frequency": 1
                            }
                        )
                        logger.warning(f"🚨 CAUGHT CONNECTION: {remote_ip}:{remote_port} (PID: {conn.pid})")
                        
        except psutil.AccessDenied:
            # On Windows, some system-level processes require Admin rights to read
            pass
        except Exception as e:
            logger.error(f"Error scanning network connections: {e}")

    def get_active_connections(self) -> List[Dict]:
        """Returns a snapshot of current established network connections."""
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    connections.append({
                        "laddr": f"{conn.laddr.ip}:{conn.laddr.port}",
                        "raddr": f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A",
                        "status": conn.status,
                        "pid": conn.pid or "N/A"
                    })
        except Exception as e:
            logger.error(f"Could not retrieve network connections: {e}")
        return connections

    def start(self):
        """Starts the network monitoring thread."""
        if not self.is_running:
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            logger.info("NetworkMonitor started.")

    def stop(self):
        """Stops the network monitoring thread."""
        if self.is_running:
            self.is_running = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=2)
            logger.info("NetworkMonitor stopped.")

    def get_network_stats(self):
        """Returns the current tracked connections and their frequencies."""
        # Sort by frequency (highest first)
        sorted_connections = sorted(
            [{"ip": ip, "port": port, "frequency": count} 
             for (ip, port), count in self.connection_frequency.items()],
            key=lambda x: x["frequency"], 
            reverse=True
        )
        return sorted_connections