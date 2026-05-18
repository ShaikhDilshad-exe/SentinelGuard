"""
Process Monitoring Module
Continuously monitors running processes and detects suspicious patterns.
Updated to support central event collection.
"""

import time
import logging
import psutil
import asyncio
import threading
from typing import Dict, List, Optional, Callable, Set
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import deque

logger = logging.getLogger(__name__)

@dataclass
class ProcessInfo:
    """Process information snapshot"""
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    num_threads: int
    status: str
    timestamp: str

class SuspiciousPattern:
    """Represents a detected suspicious pattern"""
    def __init__(self, pattern_type: str, process_info: ProcessInfo, severity: str = "medium"):
        self.pattern_type = pattern_type
        self.process_info = process_info
        self.severity = severity
        self.timestamp = datetime.now().isoformat()

class ProcessMonitor:
    """Monitor system processes in real-time and detect anomalies"""
    
    KNOWN_PROCESSES = {
        'svchost.exe', 'csrss.exe', 'services.exe', 'explorer.exe',
        'winlogon.exe', 'kernel32.dll', 'ntoskrnl.exe', 'lsass.exe',
        'wininit.exe', 'spoolsv.exe', 'System', 'Idle', 'Registry',
        'smss.exe', 'crss.exe', 'python.exe', 'java.exe', 'node.exe',
        'chrome.exe', 'firefox.exe', 'outlook.exe', 'word.exe', 'excel.exe'
    }
    
    def __init__(
        self,
        cpu_spike_threshold: float = 80.0,
        memory_spike_threshold: float = 85.0,
        history_size: int = 10,
        polling_interval: float = 2.0,  # Increased slightly to reduce overhead
        event_collector=None            # Added for central integration
    ):
        self.cpu_spike_threshold = cpu_spike_threshold
        self.memory_spike_threshold = memory_spike_threshold
        self.history_size = history_size
        self.polling_interval = polling_interval
        self.event_collector = event_collector
        
        self.processes: Dict[int, ProcessInfo] = {}
        self.process_history: Dict[int, deque] = {}
        self.suspicious_alerts: List[SuspiciousPattern] = []
        
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks: List[Callable] = []
        self.lock = threading.RLock()

    def start(self) -> bool:
        if self.monitoring:
            return False
        try:
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="ProcessMonitor"
            )
            self.monitor_thread.start()
            logger.info("Process monitoring started")
            return True
        except Exception as e:
            logger.error(f"Failed to start process monitoring: {e}")
            self.monitoring = False
            return False

    def stop(self) -> bool:
        if not self.monitoring:
            return False
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Process monitoring stopped")
        return True

    def _monitor_loop(self) -> None:
        while self.monitoring:
            try:
                self._scan_processes()
                time.sleep(self.polling_interval) # Standard sleep for thread
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")

    def _scan_processes(self) -> None:
        try:
            current_pids = set()
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    with proc.oneshot():
                        pid = proc.pid
                        current_pids.add(pid)
                        process_info = self._get_process_info(proc)
                        
                        with self.lock:
                            self.processes[pid] = process_info
                            
                            # INTEGRATION: Send to EventCollector
                            if self.event_collector:
                                self.event_collector.add_event(
                                    event_type="process",
                                    metadata=asdict(process_info)
                                )

                            if pid not in self.process_history:
                                self.process_history[pid] = deque(maxlen=self.history_size)
                            self.process_history[pid].append(process_info)
                            
                            patterns = self._detect_patterns(pid, process_info)
                            if patterns:
                                for pattern in patterns:
                                    self._handle_alert(pattern)
                
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            with self.lock:
                removed_pids = set(self.processes.keys()) - current_pids
                for pid in removed_pids:
                    self.processes.pop(pid, None)
                    self.process_history.pop(pid, None)
        except Exception as e:
            logger.error(f"Error scanning processes: {e}")

    def _get_process_info(self, proc: psutil.Process) -> ProcessInfo:
        try:
            mem_info = proc.memory_info()
            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                cpu_percent=proc.cpu_percent(interval=None),
                memory_percent=proc.memory_percent(),
                memory_mb=mem_info.rss / (1024 * 1024),
                num_threads=proc.num_threads(),
                status=proc.status(),
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return ProcessInfo(proc.pid, "unknown", 0.0, 0.0, 0.0, 0, "unknown", datetime.now().isoformat())

    def _detect_patterns(self, pid: int, process_info: ProcessInfo) -> List[SuspiciousPattern]:
        patterns = []
        if process_info.cpu_percent > self.cpu_spike_threshold:
            patterns.append(SuspiciousPattern("cpu_spike", process_info, "high" if process_info.cpu_percent > 95 else "medium"))
        
        if process_info.memory_percent > self.memory_spike_threshold:
            patterns.append(SuspiciousPattern("memory_spike", process_info, "high" if process_info.memory_percent > 95 else "medium"))
            
        if not self._is_known_process(process_info.name):
            if process_info.num_threads > 50 or process_info.memory_percent > 50:
                patterns.append(SuspiciousPattern("unknown_process", process_info, "medium"))
        return patterns

    def _is_known_process(self, process_name: str) -> bool:
        name_lower = process_name.lower()
        return any(name_lower == known.lower() for known in self.KNOWN_PROCESSES)

    def _handle_alert(self, pattern: SuspiciousPattern) -> None:
        with self.lock:
            self.suspicious_alerts.append(pattern)
            if len(self.suspicious_alerts) > 1000:
                self.suspicious_alerts.pop(0)
            for callback in self.callbacks:
                try: callback(pattern)
                except: pass

    def register_callback(self, callback: Callable) -> None:
        with self.lock:
            if callback not in self.callbacks: self.callbacks.append(callback)

    def get_suspicious_alerts(self, limit: int = 100) -> List[dict]:
        with self.lock:
            alerts = list(self.suspicious_alerts)
        alerts.sort(key=lambda a: a.timestamp, reverse=True)
        return [{"pattern_type": a.pattern_type, "severity": a.severity, "timestamp": a.timestamp, "process": asdict(a.process_info)} for a in alerts[:limit]]

    # Helper methods for API usage
    def get_running_processes(self, limit: int = None) -> List[dict]:
        with self.lock:
            processes = [asdict(p) for p in self.processes.values()]
        processes.sort(key=lambda p: p['memory_percent'], reverse=True)
        return processes[:limit] if limit else processes