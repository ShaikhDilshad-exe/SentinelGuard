"""
Heuristic Analyzer Module
Hybrid detection engine combining rule-based heuristics and machine learning.
"""

import logging
import numpy as np
import os
from typing import Dict, List, Any
from ml_model.threat_classifier import ThreatClassifier
from ml_model.feature_extractor import FeatureExtractor

logger = logging.getLogger(__name__)

class HeuristicAnalyzer:
    """
    Analyzes system events using a dual-layer approach:
    1. Rule-based Heuristics (known patterns)
    2. Machine Learning Anomaly Detection (behavioral outliers)
    """
    
    def __init__(self, model_path: str = "ml_model/sentinel_model.pkl"):
        """Initialize the hybrid analyzer."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        absolute_model_path = os.path.join(project_root, model_path)
        
        # Initialize ML components[cite: 10]
        self.ml_classifier = ThreatClassifier(model_path=absolute_model_path)
        self.feature_extractor = FeatureExtractor()
        
        # Heuristic Thresholds[cite: 10]
        self.thresholds = {
            "network_beaconing": 5,
            "cpu_spike": 80.0,
            "mem_spike": 85.0,
            "high_entropy": 7.5,
            "ransomware_file_count": 3  # Trigger after 3 .locked files[cite: 10]
        }

    def analyze_behavior(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Performs batch analysis to determine security status[cite: 10]."""
        matched_rules = []
        risk_score = 0.0
        explanation = []
        
        # --- LAYER 1: MACHINE LEARNING ---
        snapshot = self.feature_extractor.extract_features_from_events(events)
        if snapshot['total_events'] > 0:
            ml_result = self.ml_classifier.predict(snapshot)
            if ml_result.get("is_anomaly"):
                risk_score += (ml_result.get("anomaly_score", 0) / 2) #[cite: 10]
                explanation.append(f"AI Detection: Behavioral anomaly caught ({ml_result['anomaly_score']}%).")

        # --- LAYER 2: RULE-BASED HEURISTICS ---
        heuristics = self._check_heuristics(events, snapshot)
        for rule in heuristics:
            matched_rules.append(rule)
            # Critical rules add more weight to the risk score[cite: 10]
            weight = 50.0 if rule['risk'] == "critical" else 25.0
            risk_score += weight
            explanation.append(f"Heuristic Match: {rule['reason']}")

        # --- FINAL OUTPUT ---
        confidence_score = min(risk_score, 100.0) 
        threat_level = self._get_threat_level(confidence_score)
        
        return {
            "threat_level": threat_level,
            "confidence_score": round(confidence_score, 2),
            "explanation": " | ".join(explanation) if explanation else "System activity appears normal.",
            "matched_rules": matched_rules,
            "snapshot_data": snapshot,
            "source": "Heuristic Analyzer"  # <--- ADD THIS LINE HERE
        }

    def _check_heuristics(self, events: List[Dict], snapshot: Dict) -> List[Dict]:
        """Check for simple, rule-based threat patterns."""
        rules = []

        # --- BRUTE-FORCE RANSOMWARE RULE ---
        locked_files = []
        for e in events:
            # Convert the entire event to a lowercase string and search it
            event_string = str(e).lower()
            
            # If the string contains our extension, flag it immediately
            if '.locked' in event_string:
                locked_files.append(e)

        if len(locked_files) >= 1: 
            rules.append({
                "rule": "RANSOMWARE_PATTERN_DETECTED",
                "reason": f"Ransomware Alert! Caught {len(locked_files)} file event(s) involving '.locked' extensions.",
                "risk": "critical"
            })

        # --- Rule: CPU Spike ---
        if snapshot.get('max_cpu_percent', 0) > self.thresholds.get('cpu_spike', 80):
            rules.append({
                "rule": "CPU_SPIKE_DETECTED",
                "reason": f"High CPU usage of {snapshot['max_cpu_percent']}% observed.",
                "risk": "medium"
            })
        
        # --- Rule: High File Entropy ---
        if snapshot.get('avg_entropy', 0) > self.thresholds.get('high_entropy', 7.5):
            rules.append({
                "rule": "HIGH_FILE_ENTROPY",
                "reason": f"File operations involve high entropy ({snapshot['avg_entropy']:.2f}), suggesting encryption.",
                "risk": "high"
            })

        # --- REFINED NETWORK BEACONING RULE ---
        # Filter specifically for events containing network data to avoid CPU overlap
        net_events = [e for e in events if 'raddr' in str(e) or e.get('type') == 'network']
        ip_counts = {}
        
        for e in net_events:
            meta = e.get('metadata', e)
            raw_ip = meta.get('destination_ip') or meta.get('raddr')
            
            if raw_ip:
                ip = None
                
                # Handle psutil tuple format: e.g., ('8.8.8.8', 53)
                if isinstance(raw_ip, (tuple, list)) and len(raw_ip) > 0:
                    ip = str(raw_ip[0])
                    
                # Handle standard string format: e.g., "8.8.8.8:53"
                elif isinstance(raw_ip, str):
                    ip = raw_ip.split(':')[0].replace("'", "").replace("(", "").strip()
                
                if ip:
                    ip_counts[ip] = ip_counts.get(ip, 0) + 1
        
        for ip, count in ip_counts.items():
            if count >= 5: # If 5 or more connections to the same IP, trigger alert
                rules.append({
                    "rule": "NETWORK_BEACONING_SUSPECTED",
                    "reason": f"Network Beaconing: {count} connections to {ip} detected.",
                    "risk": "medium" # Set to medium to match your LiveAlerts UI chip
                })
            
        return rules

    def _get_threat_level(self, score: float) -> str:
        """Categorize risk score into a threat level[cite: 10]."""
        if score > 75: return "critical"
        if score > 50: return "high"
        if score > 25: return "medium"
        if score > 0: return "low"
        return "none"