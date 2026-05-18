import os
import time
from pathlib import Path

# Target the safe Quarantine Zone
TARGET_DIR = Path(r"C:\Users\Heramb\Coding_Folder\SEM2_CAPSTONE\SentinelGuard\Sentinel_Test")

# Create the folder if it doesn't exist
TARGET_DIR.mkdir(parents=True, exist_ok=True)
print(f"[*] Generating Ransomware Files in: {TARGET_DIR}")

for i in range(5):
    file_path = TARGET_DIR / f"test_threat_{i}.locked"
    random_data = os.urandom(1024 * 1024) 
    file_path.write_bytes(random_data)
    print(f"    [+] Created: {file_path.name}")
    time.sleep(0.5)

print("[*] Simulation finished.")