#!/usr/bin/env python
"""Quick test script for process monitoring endpoints"""

import json
import urllib.request

def test_endpoints():
    """Test monitoring endpoints"""
    
    # Test high CPU processes
    print("=== HIGH CPU PROCESSES ===")
    r = urllib.request.urlopen('http://localhost:8000/api/monitoring/processes/high-cpu')
    data = json.load(r)
    print(f"Found {data['count']} processes with high CPU usage\n")
    for p in data['processes'][:5]:
        print(f"  - {p['name']} (PID: {p['pid']}) - CPU: {p['cpu_percent']}%")
    
    print("\n=== SUSPICIOUS ALERTS ===")
    r = urllib.request.urlopen('http://localhost:8000/api/monitoring/alerts/suspicious?limit=5')
    data = json.load(r)
    print(f"Found {data['count']} suspicious alerts\n")
    for a in data['alerts'][:3]:
        print(f"  - {a['pattern_type']} ({a['severity']}) - {a['process']['name']}")
    
    print("\n=== SYSTEM STATS ===")
    r = urllib.request.urlopen('http://localhost:8000/api/monitoring/system-stats')
    data = json.load(r)
    print(f"  CPU Usage: {data['cpu_usage']}%")
    print(f"  Memory Usage: {data['memory_usage']}%")
    print(f"  Active Processes: {data['active_processes']}")
    print(f"  Suspicious Alerts: {data['suspicious_alerts']}")

if __name__ == "__main__":
    test_endpoints()
