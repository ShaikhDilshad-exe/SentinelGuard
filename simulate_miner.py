import multiprocessing
import time

def stress_cpu():
    """An infinite loop that forces the CPU to work at 100%"""
    while True:
        pass

if __name__ == '__main__':
    print("[*] Starting CPU Stress Test (Simulating Cryptominer)...")
    
    # Start processes on all available CPU cores
    processes = []
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=stress_cpu)
        p.start()
        processes.append(p)
    
    # Let the CPU spike for 10 seconds so the monitor logs it
    time.sleep(10) 
    
    print("[*] Stopping CPU Stress Test...")
    for p in processes:
        p.terminate()
    print("[*] Miner simulation complete!")