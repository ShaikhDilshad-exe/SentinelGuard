"""
Centralized Dependency Management
Initializes and holds shared instances of core components like monitors and managers.
This prevents circular imports between the main app and the API routes.
"""
from .alerts.alert_manager import AlertManager
from .utils.event_collector import EventCollector
from .monitoring.process_monitor import ProcessMonitor
from .utils.config import config
from .monitoring.file_monitor import FileMonitor
from .monitoring.network_monitor import NetworkMonitor
from .detection.heuristic_analyzer import HeuristicAnalyzer
from .utils.websocket_manager import manager as websocket_manager

# ---------------------------------------------------------
# INITIALIZE CORE SYSTEMS
# ---------------------------------------------------------
alert_manager = AlertManager()
event_collector = EventCollector(max_size=5000)
analyzer = HeuristicAnalyzer()

# ---------------------------------------------------------
# INITIALIZE MONITORS
# ---------------------------------------------------------
file_monitor = FileMonitor(watch_paths=config.WATCH_PATHS)
network_monitor = NetworkMonitor(alert_manager=alert_manager)
network_monitor.event_collector = event_collector
process_monitor = ProcessMonitor(event_collector=event_collector)
