"""
Feature Extraction Module
Extracts relevant features from files and processes for ML model input.
"""

import logging
import hashlib
from typing import Dict
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeatureExtractor:
    """Extracts features from files and system events for the ML model."""
    
    @staticmethod
    def extract_file_features(file_path: str) -> Dict[str, float]:
        """
        Extract features from a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            # File size
            import os
            features['file_size'] = os.path.getsize(file_path)
            
            # File entropy (indicator of compression/encryption)
            with open(file_path, 'rb') as f:
                data = f.read(8192)  # Read first 8KB
                features['entropy'] = FeatureExtractor._calculate_entropy(data)
            
            # File type indicators
            ext = file_path.split('.')[-1].lower()
            features['is_executable'] = 1.0 if ext in ['exe', 'dll', 'sys'] else 0.0
            
            # More features can be added (magic bytes, PE headers, etc.)
            
        except Exception as e:
            logger.error(f"Error extracting file features: {e}")
        
        return features
    
    @staticmethod
    def extract_process_features(process_info: Dict) -> Dict[str, float]:
        """
        Extract features from a running process
        
        Args:
            process_info: Process information dictionary
            
        Returns:
            Dictionary of extracted features
        """
        features = {}
        
        try:
            features['cpu_percent'] = process_info.get('cpu_percent', 0.0)
            features['memory_percent'] = process_info.get('memory_percent', 0.0)
            features['num_threads'] = process_info.get('num_threads', 0)
            features['num_fds'] = process_info.get('num_fds', 0)
            
        except Exception as e:
            logger.error(f"Error extracting process features: {e}")
        
        return features
    
    @staticmethod
    def _calculate_entropy(data: bytes) -> float:
        """
        Calculate Shannon entropy of data
        
        Args:
            data: Byte data
            
        Returns:
            Entropy value (0-8 for bytes)
        """
        if not data:
            return 0.0
        
        entropy = 0.0
        for i in range(256):
            probability = data.count(bytes([i])) / len(data)
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        return entropy
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'sha256') -> str:
        """
        Calculate hash of a file
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use
            
        Returns:
            Hex digest of the file hash
        """
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
        except Exception as e:
            logger.error(f"Error calculating file hash: {e}")
        
        return hash_obj.hexdigest()

    def extract_features_from_events(self, events: list) -> Dict:
        """
        Processes a batch of events and aggregates them into a single feature vector (snapshot).
        """
        if not events:
            return {"total_events": 0}

        # Segregate events by type
        process_events = [e['metadata'] for e in events if e['type'] == 'process' and 'metadata' in e]
        file_events = [e['metadata'] for e in events if e['type'] == 'file' and 'metadata' in e]

        # --- Aggregate Process Features ---
        if process_events:
            avg_cpu = np.mean([p.get('cpu_percent', 0) for p in process_events])
            avg_mem = np.mean([p.get('memory_percent', 0) for p in process_events])
            avg_threads = int(np.mean([p.get('num_threads', 0) for p in process_events]))
            max_cpu = np.max([p.get('cpu_percent', 0) for p in process_events])
            max_mem = np.max([p.get('memory_percent', 0) for p in process_events])
        else:
            # Provide default float values to prevent NaN results
            avg_cpu, avg_mem, avg_threads, max_cpu, max_mem = 0.0, 0.0, 0, 0.0, 0.0
            
        # --- Aggregate File Features ---
        # Ensure entropy values are not None before calculating mean
        entropies = [f.get('entropy') for f in file_events if f.get('entropy') is not None]
        if entropies:
            avg_entropy = np.mean(entropies)
        else:
            avg_entropy = 3.0 # Default to a "normal" entropy

        # --- Construct the Snapshot ---
        snapshot = {
            # --- Primary features for the ML model ---
            "cpu_percent": avg_cpu,
            "memory_percent": avg_mem,
            "num_threads": avg_threads,
            "entropy": avg_entropy,
            
            # --- Secondary features for heuristics & context ---
            "max_cpu_percent": max_cpu,
            "max_memory_percent": max_mem,
            "total_events": len(events),
            "process_event_count": len(process_events),
            "file_event_count": len(file_events)
        }
        return snapshot
