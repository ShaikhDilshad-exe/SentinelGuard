"""
File System Monitoring Module
Monitors file system activities like creation, modification, deletion, and access.
Detects suspicious patterns like rapid changes and suspicious file extensions.
"""

import logging
import threading
import time
from pathlib import Path
from typing import Callable, List, Dict, Set, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, deque
from enum import Enum

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler as WatchdogHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logging.warning("watchdog not installed. File monitoring disabled.")

logger = logging.getLogger(__name__)


class FileEventType(Enum):
    """File system event types"""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileEvent:
    """File system event record"""
    event_type: str
    file_path: str
    file_name: str
    timestamp: str
    file_size: Optional[int] = None
    is_directory: bool = False


class SuspiciousFilePattern:
    """Detected suspicious file pattern"""
    
    SUSPICIOUS_EXTENSIONS = {
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr',
        '.vbs', '.js', '.ps1', '.psm1', '.msi', '.dll',
        '.sys', '.drv', '.cpl', '.reg', '.lnk', '.jar',
        '.py', '.pl', '.php', '.asp', '.jsp', '.locked'
    }
    
    def __init__(self, pattern_type: str, file_path: str, severity: str = "medium"):
        self.pattern_type = pattern_type
        self.file_path = file_path
        self.severity = severity
        self.timestamp = datetime.now().isoformat()


class FileSystemEventHandler(WatchdogHandler):
    """Handles file system events from watchdog"""
    
    def __init__(self, callback: Callable):
        self.callback = callback
    
    def on_created(self, event):
        if not event.is_directory:
            self.callback(FileEventType.CREATED, event.src_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            self.callback(FileEventType.MODIFIED, event.src_path)
    
    def on_deleted(self, event):
        if not event.is_directory:
            self.callback(FileEventType.DELETED, event.src_path)
    
    def on_moved(self, event):
        if not event.is_directory:
            self.callback(FileEventType.MOVED, event.dest_path)


class FileMonitor:
    """Monitor file system activities in real-time"""
    
    def __init__(
        self,
        watch_paths: List[str] = None,
        rapid_change_threshold: int = 10,
        time_window_seconds: int = 5
    ):
        """
        Initialize file monitor
        
        Args:
            watch_paths: List of paths to monitor (default: Downloads, AppData)
            rapid_change_threshold: Number of changes to flag as rapid
            time_window_seconds: Time window for rapid change detection
        """
        if not WATCHDOG_AVAILABLE:
            logger.warning("watchdog not available. Install with: pip install watchdog")
        
        # Default paths to monitor
        if watch_paths is None:
            watch_paths = self._get_default_watch_paths()
        
        self.watch_paths = [Path(p) for p in watch_paths if Path(p).exists()]
        self.rapid_change_threshold = rapid_change_threshold
        self.time_window_seconds = time_window_seconds
        
        # Event tracking
        self.file_events: List[FileEvent] = []
        self.recent_changes: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.suspicious_patterns: List[SuspiciousFilePattern] = []
        
        # Monitoring control
        self.monitoring = False
        self.observer = None
        self.callbacks: List[Callable] = []
        self.lock = threading.RLock()
    
    def _get_default_watch_paths(self) -> List[str]:
        """Get default paths to monitor"""
        paths = []
        home = Path.home()
        
        # Downloads folder
        downloads = home / "Downloads"
        if downloads.exists():
            paths.append(str(downloads))
        
        # Desktop
        desktop = home / "Desktop"
        if desktop.exists():
            paths.append(str(desktop))
        
        # AppData\Local\Temp
        appdata = home / "AppData" / "Local" / "Temp"
        if appdata.exists():
            paths.append(str(appdata))
        
        return paths if paths else [str(home)]
    
    def start(self) -> bool:
        """Start file system monitoring"""
        if not WATCHDOG_AVAILABLE:
            logger.error("watchdog not available. Cannot start monitoring.")
            return False
        
        if self.monitoring:
            logger.warning("File monitoring already running")
            return False
        
        try:
            self.observer = Observer()
            
            # Register handlers for each watch path
            for path in self.watch_paths:
                handler = FileSystemEventHandler(self._on_file_event)
                self.observer.schedule(handler, str(path), recursive=True)
            
            self.observer.start()
            self.monitoring = True
            logger.info(f"File monitoring started for {len(self.watch_paths)} paths")
            return True
        
        except Exception as e:
            logger.error(f"Failed to start file monitoring: {e}")
            self.monitoring = False
            return False
    
    def stop(self) -> bool:
        """Stop file system monitoring"""
        if not self.monitoring:
            return False
        
        try:
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5)
            self.monitoring = False
            logger.info("File monitoring stopped")
            return True
        except Exception as e:
            logger.error(f"Error stopping file monitoring: {e}")
            return False
    
    def _on_file_event(self, event_type: FileEventType, file_path: str) -> None:
        """Handle file system event"""
        try:
            from backend.dependencies import analyzer, alert_manager
            
            file_path_obj = Path(file_path)
            
            # Create event record
            event = FileEvent(
                event_type=event_type.value,
                file_path=file_path,
                file_name=file_path_obj.name,
                timestamp=datetime.now().isoformat(),
                file_size=self._get_file_size(file_path) if event_type != FileEventType.DELETED else None,
                is_directory=file_path_obj.is_dir()
            )

            # Analyze behavior and create alerts if needed
            analysis = analyzer.analyze_behavior([{
                "type": "file",
                "file_path": file_path,
                "event_type": event_type.value
            }])
            
            print(f"[DEBUG] Analysis result: {analysis}")
            
            if analysis.get("threat_level") in ["low", "medium", "high", "critical"]:
                alert_manager.create_alert(
                    severity=analysis["threat_level"],
                    message=f"Suspicious file activity detected: {file_path}",
                    source="FileMonitor",
                    threat_data=analysis
                )
                
                print(f"[ALERT CREATED] {file_path}")

            
            
            with self.lock:
                self.file_events.append(event)
                if len(self.file_events) > 1000:
                    self.file_events.pop(0)
                
                # Track recent changes by directory
                dir_key = str(file_path_obj.parent)
                self.recent_changes[dir_key].append(event)
            
            # Detect suspicious patterns
            patterns = self._detect_patterns(event)
            if patterns:
                for pattern in patterns:
                    self._handle_alert(pattern)
            
            # Notify subscribers
            self._notify_subscribers(event)
        
        except Exception as e:
            logger.error(f"Error handling file event: {e}")
    
    def _get_file_size(self, file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except:
            return None
    
    def _detect_patterns(self, event: FileEvent) -> List[SuspiciousFilePattern]:
        """Detect suspicious patterns"""
        patterns = []
        
        try:
            # Check for suspicious file extensions
            file_ext = Path(event.file_path).suffix.lower()
            if file_ext in SuspiciousFilePattern.SUSPICIOUS_EXTENSIONS:
                patterns.append(SuspiciousFilePattern(
                    pattern_type="suspicious_extension",
                    file_path=event.file_path,
                    severity="high" if file_ext in {'.exe', '.bat', '.cmd', '.ps1'} else "medium"
                ))
            
            # Check for rapid file changes (ransomware-like behavior)
            dir_key = str(Path(event.file_path).parent)
            if dir_key in self.recent_changes:
                changes_in_window = []
                current_time = datetime.fromisoformat(event.timestamp)
                
                for recorded_event in self.recent_changes[dir_key]:
                    recorded_time = datetime.fromisoformat(recorded_event.timestamp)
                    time_diff = (current_time - recorded_time).total_seconds()
                    
                    if time_diff <= self.time_window_seconds:
                        changes_in_window.append(recorded_event)
                
                if len(changes_in_window) >= self.rapid_change_threshold:
                    patterns.append(SuspiciousFilePattern(
                        pattern_type="rapid_file_changes",
                        file_path=str(Path(event.file_path).parent),
                        severity="high"
                    ))
            
            # Detect malware-specific filenames
            if any(x in event.file_name.lower() for x in ["malware", "virus", "trojan", "hack"]):
                patterns.append(SuspiciousFilePattern(
                    pattern_type="malware_filename_detected",
                    file_path=event.file_path,
                    severity="high"
                ))
            
            # Check for suspicious file names
            if self._is_suspicious_filename(event.file_name):
                patterns.append(SuspiciousFilePattern(
                    pattern_type="suspicious_filename",
                    file_path=event.file_path,
                    severity="medium"
                ))
        
        except Exception as e:
            logger.debug(f"Error detecting patterns: {e}")
        
        return patterns
    
    def _is_suspicious_filename(self, filename: str) -> bool:
        """Check if filename is suspicious"""
        suspicious_patterns = [
            'virus', 'malware', 'trojan', 'worm', 'ransomware',
            'payload', 'exploit', 'backdoor', 'keylogger',
            'temp', 'tmp', '$' , '~'
        ]
        
        filename_lower = filename.lower()
        return any(pattern in filename_lower for pattern in suspicious_patterns)
    
    def _handle_alert(self, pattern: SuspiciousFilePattern) -> None:
        """Handle detected suspicious pattern"""
        from backend.dependencies import alert_manager
        
        with self.lock:
            self.suspicious_patterns.append(pattern)
            if len(self.suspicious_patterns) > 500:
                self.suspicious_patterns.pop(0)
        
        # Create alert for suspicious pattern
        alert_manager.create_alert(
            severity=pattern.severity,
            message=f"Suspicious file pattern detected: {pattern.pattern_type} - {pattern.file_path}",
            source="FileMonitor",
            threat_data={
                "pattern_type": pattern.pattern_type,
                "file_path": pattern.file_path,
                "severity": pattern.severity,
                "timestamp": pattern.timestamp
            }
        )
        
        print(f"[ALERT CREATED] {pattern.file_path} - {pattern.pattern_type}")
    
    def _notify_subscribers(self, event: FileEvent) -> None:
        """Notify subscribers of file event"""
        for callback in self.callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"Error in file event callback: {e}")
    
    def register_callback(self, callback: Callable[[FileEvent], None]) -> None:
        """Register callback for file events"""
        with self.lock:
            if callback not in self.callbacks:
                self.callbacks.append(callback)
    
    def unregister_callback(self, callback: Callable) -> None:
        """Unregister file event callback"""
        with self.lock:
            if callback in self.callbacks:
                self.callbacks.remove(callback)
    
    def get_file_events(self, limit: int = 100) -> List[dict]:
        """
        Get recent file events
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of file events
        """
        with self.lock:
            events = list(self.file_events)
        
        events.sort(key=lambda e: e.timestamp, reverse=True)
        return [asdict(e) for e in events[:limit]]
    
    def get_suspicious_patterns(self, limit: int = 50) -> List[dict]:
        """
        Get detected suspicious patterns
        
        Args:
            limit: Maximum number of patterns to return
            
        Returns:
            List of suspicious patterns
        """
        with self.lock:
            patterns = list(self.suspicious_patterns)
        
        patterns.sort(key=lambda p: p.timestamp, reverse=True)
        return [
            {
                "pattern_type": p.pattern_type,
                "file_path": p.file_path,
                "severity": p.severity,
                "timestamp": p.timestamp
            }
            for p in patterns[:limit]
        ]
    
    def get_events_by_type(self, event_type: str, limit: int = 50) -> List[dict]:
        """Get events filtered by type"""
        with self.lock:
            filtered = [e for e in self.file_events if e.event_type == event_type]
        
        filtered.sort(key=lambda e: e.timestamp, reverse=True)
        return [asdict(e) for e in filtered[:limit]]
    
    def add_watch_path(self, path: str) -> bool:
        """Add a new path to monitor"""
        try:
            path_obj = Path(path)
            if not path_obj.exists():
                logger.warning(f"Path does not exist: {path}")
                return False
            
            if path_obj in self.watch_paths:
                return True
            
            if self.monitoring and WATCHDOG_AVAILABLE:
                handler = FileSystemEventHandler(self._on_file_event)
                self.observer.schedule(handler, str(path_obj), recursive=True)
            
            self.watch_paths.append(path_obj)
            logger.info(f"Added watch path: {path}")
            return True
        except Exception as e:
            logger.error(f"Error adding watch path: {e}")
            return False
    
    def remove_watch_path(self, path: str) -> bool:
        """Remove a path from monitoring"""
        try:
            path_obj = Path(path)
            if path_obj in self.watch_paths:
                self.watch_paths.remove(path_obj)
                logger.info(f"Removed watch path: {path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error removing watch path: {e}")
            return False
    
    def get_watch_paths(self) -> List[str]:
        """Get list of monitored paths"""
        return [str(p) for p in self.watch_paths]
