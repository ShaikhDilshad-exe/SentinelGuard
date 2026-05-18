"""
Utils Module - Utility functions and helpers
"""

from .config import config, WATCH_PATHS, MONITORING_INTERVAL
from .logger import setup_logger  # <--- Fixed this line to match your file name!
from .event_collector import EventCollector

# Expose these utilities so they can be imported directly from 'utils'
__all__ = [
    "config",
    "WATCH_PATHS",
    "MONITORING_INTERVAL",
    "setup_logger",
    "EventCollector"
]