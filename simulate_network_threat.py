import socket
import time
import threading

TARGET_PORT = 9999

def dummy_c2_server():
    """A fake local server to receive the connection"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', TARGET_PORT))
    s.listen(1)
    conn, addr = s.accept()
    time.sleep(15) # Hold the connection open
    conn.close()
    s.close()

# Start the fake server in the background
threading.Thread(target=dummy_c2_server, daemon=True).start()
time.sleep(1) # Give the server a second to start

print(f"[*] Connecting to local fake C2 server on port {TARGET_PORT}...")

try:
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    c.connect(('127.0.0.1', TARGET_PORT))
    print("    [+] Connection ESTABLISHED internally! Holding for 15 seconds...")
    time.sleep(15) 
    c.close()
    print("    [-] Connection closed.")
except Exception as e:
    print(f"    [!] Failed: {e}")