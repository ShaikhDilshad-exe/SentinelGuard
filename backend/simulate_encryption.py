import os
import time
from pathlib import Path

# Change this line in simulate_encryption.py
TARGET_DIR = Path(".")
TARGET_DIR.mkdir(parents=True, exist_ok=True)

print("[*] Generating Ransomware Files...")

# Let's create 5 files to ensure it crosses any thresholds
for i in range(5):
    # CHANGED: .bin is now .locked
    file_path = TARGET_DIR / f"high_entropy_data_{i}.locked" 
    
    random_data = os.urandom(1024 * 1024) 
    file_path.write_bytes(random_data)
    print(f"    [+] Wrote highly entropic data to {file_path.name}")
    time.sleep(1)

print("[*] Encryption simulation complete.")