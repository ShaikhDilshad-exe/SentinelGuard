import time
from pathlib import Path

# IMPORTANT: Ensure this matches your configured watch path exactly
TARGET_DIR = Path(r"D:\capstone\SentinelGuard\Sentinel_Test")
# Ensure the directory exists before attacking
TARGET_DIR.mkdir(parents=True, exist_ok=True)

print(f"[*] Simulating rapid ransomware burst in {TARGET_DIR}...")

# Create 15 files almost instantly
for i in range(15):
    file_path = TARGET_DIR / f"fake_encrypted_file_{i}.locked"
    file_path.write_text("Simulating encrypted data...") 
    print(f"    Created: {file_path.name}")
    
    # Micro-sleep: 0.02s is fast enough to simulate an attack (0.3s total execution)
    # but prevents the OS from merging the creation events into a single directory update.
    time.sleep(0.02) 

print("[*] Attack simulation complete. Check your dashboard for Live Alerts!")