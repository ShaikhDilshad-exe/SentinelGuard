import socket
import time

print("[*] Simulating LOUD Network Beaconing...")
TARGET_IP = "8.8.8.8"
PORT = 53
open_sockets = []

# Open 10 connections and DO NOT close them immediately
for i in range(10): 
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect((TARGET_IP, PORT))
        open_sockets.append(s)
        print(f"    [+] Connection {i+1}/10 established to {TARGET_IP}")
    except Exception as e:
        print(f"Failed: {e}")

# Hold the connections open for 10 seconds so the monitor catches them
print("[*] Holding connections open so the Sentinel camera catches them...")
time.sleep(10)

# Cleanup
for s in open_sockets:
    s.close()
print("[*] Beaconing simulation complete.")