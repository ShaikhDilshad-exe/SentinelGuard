"""
Detection Module - Threat detection and analysis
"""

from .heuristic_analyzer import HeuristicAnalyzer
from .threat_detector import ThreatDetector

__all__ = ["HeuristicAnalyzer", "ThreatDetector"]