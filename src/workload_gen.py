import time
import random
import resource
import sys
import csv
import os

def run_workload(buffer_size_mb=200, iterations=2_000_000, hot_fraction=0.2, hot_access_prob=0.8):
    """
    Simulates a memory access pattern with a 'hot' region (frequently accessed)
    and a 'cold' region (rarely accessed).
    """
    buffer_size = buffer_size_mb * 1024 * 1024  # convert MB to bytes
    print(f"Allocating buffer of {buffer_size_mb} MB...")

    # Allocate the buffer as a bytearray (each element is 1 byte)
    buffer = bytearray(buffer_size)

    hot_region_size = int(buffer_size * hot_fraction)

    # Get starting resource usage (for page fault tracking)
    usage_start = resource.getrusage(resource.RUSAGE_SELF)

    start_time = time.time()

    for _ in range(iterations):
        if random.random() < hot_access_prob:
            # Access hot region
            idx = random.randint(0, hot_region_size - 1)
        else:
            # Access cold region
            idx = random.randint(hot_region_size, buffer_size - 1)

        # Simulate a memory "touch" — read and write
        buffer[idx] = (buffer[idx] + 1) % 256

    end_time = time.time()
    usage_end = resource.getrusage(resource.RUSAGE_SELF)

    total_time_ms = (end_time - start_time) * 1000
    minor_faults = usage_end.ru_minflt - usage_start.ru_minflt
    major_faults = usage_end.ru_majflt - usage_start.ru_majflt

    return total_time_ms, minor_faults, major_faults


def main():
    num_runs = 5
    results = []

    for run_id in range(1, num_runs + 1):
        print(f"\n--- Run {run_id} ---")
        total_time_ms, minor_faults, major_faults = run_workload()
        print(f"Time: {total_time_ms:.2f} ms | Minor faults: {minor_faults} | Major faults: {major_faults}")
        results.append([run_id, round(total_time_ms, 2), minor_faults, major_faults])

    # Save results to CSV
    os.makedirs("results/baseline", exist_ok=True)
    csv_path = "results/baseline/summary.csv"

    with open(csv_path, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "total_time_ms", "minor_faults", "major_faults"])
        writer.writerows(results)

    print(f"\nResults saved to {csv_path}")


if __name__ == "__main__":
    main()
