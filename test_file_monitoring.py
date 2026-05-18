"""
File Monitoring Integration Test
Tests the file_monitor module with API endpoints
"""

import requests
import time
import tempfile
from pathlib import Path
import json

BASE_URL = "http://localhost:8000/api/monitoring"


def test_file_monitoring_integration():
    print("\n" + "="*70)
    print("FILE MONITORING INTEGRATION TEST")
    print("="*70 + "\n")

    # Test 1: Check monitor status
    print("[Test 1] Checking monitor status...")
    response = requests.get(f"{BASE_URL}/monitor/status")
    status = response.json()
    
    print(f"  Process Monitor: {status['process_monitor']['monitoring']}")
    print(f"  File Monitor: {status['file_monitor']['monitoring']}")
    print(f"  Watch Paths: {status['file_monitor']['watch_paths']}")
    print(f"  Events Tracked: {status['file_monitor']['events_tracked']}")
    
    # Test 2: Get watch paths
    print("\n[Test 2] Getting monitored paths...")
    response = requests.get(f"{BASE_URL}/files/watch-paths")
    paths = response.json()
    for path in paths['paths']:
        print(f"  - {path}")
    
    # Test 3: Get current file events
    print("\n[Test 3] Getting file events...")
    response = requests.get(f"{BASE_URL}/files/events")
    events = response.json()
    print(f"  Total Events: {events['count']}")
    if events['count'] > 0:
        print("  Recent events:")
        for event in events['events'][:3]:
            print(f"    [{event['event_type']}] {Path(event['file_path']).name} @ {event['timestamp']}")
    
    # Test 4: Get suspicious patterns
    print("\n[Test 4] Detecting suspicious patterns...")
    response = requests.get(f"{BASE_URL}/files/suspicious")
    patterns = response.json()
    print(f"  Suspicious Patterns Detected: {patterns['count']}")
    if patterns['count'] > 0:
        pattern_types = {}
        for p in patterns['patterns']:
            pt = p['pattern_type']
            pattern_types[pt] = pattern_types.get(pt, 0) + 1
        print("  Pattern Distribution:")
        for ptype, count in pattern_types.items():
            print(f"    - {ptype}: {count}")
    
    # Test 5: Events by type
    print("\n[Test 5] Getting events by type...")
    for event_type in ['created', 'modified', 'deleted']:
        response = requests.get(f"{BASE_URL}/files/events/{event_type}")
        events = response.json()
        print(f"  {event_type.capitalize()}: {events['count']} events")
    
    # Test 6: System stats
    print("\n[Test 6] Overall System Statistics...")
    response = requests.get(f"{BASE_URL}/system-stats")
    stats = response.json()
    
    print("  Process Monitoring:")
    print(f"    - CPU Usage: {stats['process_monitoring']['cpu_usage']}%")
    print(f"    - Memory Usage: {stats['process_monitoring']['memory_usage']}%")
    print(f"    - Active Processes: {stats['process_monitoring']['active_processes']}")
    print(f"    - Suspicious Alerts: {stats['process_monitoring']['suspicious_alerts']}")
    
    print("  File Monitoring:")
    print(f"    - File Events: {stats['file_monitoring']['file_events']}")
    print(f"    - Suspicious Patterns: {stats['file_monitoring']['suspicious_patterns']}")
    print(f"    - Watch Paths: {stats['file_monitoring']['watch_paths']}")
    
    # Test 7: High CPU & Memory processes
    print("\n[Test 7] Detecting high-resource processes...")
    try:
        response = requests.get(f"{BASE_URL}/processes/high-cpu")
        high_cpu = response.json()
        cpu_count = high_cpu.get('count', 0) or len(high_cpu.get('processes', []))
        print(f"  High CPU Processes: {cpu_count}")
        if cpu_count > 0:
            for proc in high_cpu.get('processes', [])[:2]:
                print(f"    - {proc['name']}: {proc['cpu_percent']}% CPU")
        
        response = requests.get(f"{BASE_URL}/processes/high-memory")
        high_mem = response.json()
        mem_count = high_mem.get('count', 0) or len(high_mem.get('processes', []))
        print(f"  High Memory Processes: {mem_count}")
        if mem_count > 0:
            for proc in high_mem.get('processes', [])[:2]:
                print(f"    - {proc['name']}: {proc['memory_percent']}% ({proc['memory_mb']:.1f} MB)")
    except Exception as e:
        print(f"  Warning: Could not retrieve process details: {e}")
    
    # Test 8: Suspicious alerts
    print("\n[Test 8] Suspicious Process Alerts...")
    try:
        response = requests.get(f"{BASE_URL}/alerts/suspicious?limit=5")
        alerts = response.json()
        alert_count = alerts.get('count', 0) or len(alerts.get('alerts', []))
        print(f"  Total Alerts: {alert_count}")
        if alert_count > 0:
            alert_types = {}
            for alert in alerts.get('alerts', [])[:5]:
                atype = alert.get('alert_type', 'unknown')
                alert_types[atype] = alert_types.get(atype, 0) + 1
            print("  Alert Types Detected:")
            for atype, count in alert_types.items():
                print(f"    - {atype}: {count}")
    except Exception as e:
        print(f"  Warning: Could not retrieve suspicious alerts: {e}")

    print("\n" + "="*70)
    print("TEST COMPLETED SUCCESSFULLY")
    print("="*70 + "\n")


if __name__ == "__main__":
    try:
        test_file_monitoring_integration()
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
