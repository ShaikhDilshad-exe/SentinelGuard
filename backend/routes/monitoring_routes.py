"""
Monitoring Routes
API endpoints for system and file monitoring data.
"""

import psutil # Add to top of file

from fastapi import APIRouter, HTTPException
from typing import Optional
from ..dependencies import process_monitor, file_monitor, network_monitor # Add network_monitor to imports
router = APIRouter(tags=["monitoring"])


# ==================== PROCESS MONITORING ====================

@router.get("/processes")
async def get_running_processes(limit: Optional[int] = None):
    """Get list of running processes"""
    try:
        processes = process_monitor.get_running_processes(limit=limit)
        return {"processes": processes, "count": len(processes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/{pid}")
async def get_process_info(pid: int):
    """Get detailed information about a specific process"""
    try:
        process_info = process_monitor.get_process_info(pid)
        if process_info:
            return process_info
        raise HTTPException(status_code=404, detail="Process not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/high-cpu")
async def get_high_cpu_processes(threshold: float = 80.0, limit: int = 10):
    """Get processes with high CPU usage"""
    try:
        processes = process_monitor.get_high_cpu_processes(threshold=threshold, limit=limit)
        return {"processes": processes, "count": len(processes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/processes/high-memory")
async def get_high_memory_processes(threshold: float = 85.0, limit: int = 10):
    """Get processes with high memory usage"""
    try:
        processes = process_monitor.get_high_memory_processes(threshold=threshold, limit=limit)
        return {"processes": processes, "count": len(processes)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== FILE MONITORING ====================

@router.get("/files/events")
async def get_file_events(limit: int = 100):
    """Get recent file system events"""
    try:
        events = file_monitor.get_file_events(limit=limit)
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/events/{event_type}")
async def get_events_by_type(event_type: str, limit: int = 50):
    """Get file events filtered by type (created, modified, deleted, moved)"""
    try:
        events = file_monitor.get_events_by_type(event_type, limit=limit)
        return {"events": events, "count": len(events)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/suspicious")
async def get_suspicious_file_patterns(limit: int = 50):
    """Get detected suspicious file patterns"""
    try:
        patterns = file_monitor.get_suspicious_patterns(limit=limit)
        return {"patterns": patterns, "count": len(patterns)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/watch-paths")
async def get_watch_paths():
    """Get list of monitored directories"""
    try:
        paths = file_monitor.get_watch_paths()
        return {"paths": paths, "count": len(paths)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/files/watch-paths")
async def add_watch_path(path: str):
    """Add a new directory to monitor"""
    try:
        success = file_monitor.add_watch_path(path)
        return {
            "success": success,
            "message": f"Path {'added' if success else 'failed to add'}: {path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/watch-paths")
async def remove_watch_path(path: str):
    """Remove a directory from monitoring"""
    try:
        success = file_monitor.remove_watch_path(path)
        return {
            "success": success,
            "message": f"Path {'removed' if success else 'not found'}: {path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MONITOR CONTROL ====================

@router.post("/monitor/start")
async def start_monitoring():
    """Start system and file monitoring"""
    try:
        process_started = process_monitor.start() if not process_monitor.monitoring else True
        file_started = file_monitor.start() if not file_monitor.monitoring else True
        return {
            "message": "Monitoring started",
            "status": "running",
            "process_monitor": process_started,
            "file_monitor": file_started
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor/stop")
async def stop_monitoring():
    """Stop system and file monitoring"""
    try:
        process_stopped = process_monitor.stop() if process_monitor.monitoring else True
        file_stopped = file_monitor.stop() if file_monitor.monitoring else True
        return {
            "message": "Monitoring stopped",
            "status": "stopped",
            "process_monitor": process_stopped,
            "file_monitor": file_stopped
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitor/status")
async def get_monitor_status():
    """Get monitoring status for all components"""
    return {
        "process_monitor": {
            "monitoring": process_monitor.monitoring,
            "processes_tracked": len(process_monitor.processes),
            "alerts": len(process_monitor.suspicious_alerts)
        },
        "file_monitor": {
            "monitoring": file_monitor.monitoring,
            "events_tracked": len(file_monitor.file_events),
            "suspicious_patterns": len(file_monitor.suspicious_patterns),
            "watch_paths": len(file_monitor.watch_paths)
        }
    }


# ==================== SYSTEM STATISTICS ====================

@router.get("/system-stats")
async def get_system_stats():
    """Get overall system statistics[cite: 25]"""
    try:
        processes = process_monitor.get_running_processes()
        
        # FIX: Use psutil to get actual overall system-wide usage[cite: 25]
        # This prevents the 900%+ bug by using global OS metrics[cite: 25]
        overall_cpu = psutil.cpu_percent(interval=None)
        overall_mem = psutil.virtual_memory().percent
        
        return {
            "process_monitoring": {
                "cpu_usage": overall_cpu,
                "memory_usage": overall_mem,
                "active_processes": len(processes),
                "suspicious_alerts": len(process_monitor.suspicious_alerts)
            },
            "file_monitoring": {
                "file_events": len(file_monitor.file_events),
                "suspicious_patterns": len(file_monitor.suspicious_patterns),
                "watch_paths": len(file_monitor.watch_paths)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/connections")
async def get_network_connections():
    """Get list of active network connections"""
    try:
        # Use the existing network_monitor instance from dependencies[cite: 17, 18]
        connections = network_monitor.get_active_connections()
        return connections
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))