import random
import time
from access_monitor import AccessMonitor

def run_workload_with_monitoring(buffer_size_mb=200, iterations=2_000_000,
                                   hot_fraction=0.2, hot_access_prob=0.8,
                                   page_size=4096):
    buffer_size = buffer_size_mb * 1024 * 1024
    print(f"Allocating buffer of {buffer_size_mb} MB...")

    buffer = bytearray(buffer_size)
    hot_region_size = int(buffer_size * hot_fraction)

    monitor = AccessMonitor(buffer_size, page_size=page_size)

    start_time = time.time()

    for _ in range(iterations):
        if random.random() < hot_access_prob:
            idx = random.randint(0, hot_region_size - 1)
        else:
            idx = random.randint(hot_region_size, buffer_size - 1)

        buffer[idx] = (buffer[idx] + 1) % 256
        monitor.record_access(idx)

    end_time = time.time()
    total_time_ms = (end_time - start_time) * 1000
    print(f"Workload finished in {total_time_ms:.2f} ms")

    results = monitor.save_results(hot_fraction=hot_fraction)
    return results


if __name__ == "__main__":
    run_workload_with_monitoring()
