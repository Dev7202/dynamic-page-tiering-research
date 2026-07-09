import time
import random
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from access_monitor import AccessMonitor
from tiering_policy import TieringPolicy
from migration_engine import MigrationEngine


def run_tiering_system(buffer_size_mb=200, iterations=2_000_000,
                        hot_fraction=0.2, hot_access_prob=0.8,
                        policy="frequency", page_size=4096):
    """
    Full tiering system run:
    1. Run workload with access monitoring
    2. Apply tiering policy to classify pages
    3. Migrate pages based on classification
    4. Report results
    """
    buffer_size = buffer_size_mb * 1024 * 1024
    print(f"\n{'='*50}")
    print(f"Dynamic Page Tiering System")
    print(f"Policy: {policy.upper()} | Buffer: {buffer_size_mb}MB | Iterations: {iterations:,}")
    print(f"{'='*50}\n")

    # Step 1: Allocate buffer and run workload with monitoring
    print("[Step 1] Running workload with access monitoring...")
    buffer = bytearray(buffer_size)
    hot_region_size = int(buffer_size * hot_fraction)
    monitor = AccessMonitor(buffer_size, page_size=page_size)

    # For LRU policy — track access times
    tiering_pol = TieringPolicy(policy=policy, hot_fraction=hot_fraction)
    access_times = {}

    start_time = time.time()

    for i in range(iterations):
        if random.random() < hot_access_prob:
            idx = random.randint(0, hot_region_size - 1)
        else:
            idx = random.randint(hot_region_size, buffer_size - 1)

        buffer[idx] = (buffer[idx] + 1) % 256
        monitor.record_access(idx)

        # Record access time for LRU
        page_id = idx // page_size
        tiering_pol.record_access(page_id, i)

    end_time = time.time()
    workload_time_ms = (end_time - start_time) * 1000
    print(f"Workload completed in {workload_time_ms:.2f} ms")

    # Step 2: Apply tiering policy
    print(f"\n[Step 2] Applying {policy} tiering policy...")
    access_counts = list(enumerate(monitor.access_counts))
    classified_pages = tiering_pol.classify(access_counts, current_time=iterations)

    # Step 3: Migrate pages
    print("\n[Step 3] Migrating pages between tiers...")
    engine = MigrationEngine(page_size=page_size)
    migration_time_ms, hot_migrated, cold_migrated = engine.migrate_pages(classified_pages)

    # Step 4: Save all outputs
    print("\n[Step 4] Saving results...")
    monitor.save_results(hot_fraction=hot_fraction)
    tiering_pol.save_policy_results(classified_pages)
    engine.save_migration_log()

    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY")
    print(f"{'='*50}")
    print(f"Workload time:     {workload_time_ms:.2f} ms")
    print(f"Migration time:    {migration_time_ms:.2f} ms")
    print(f"Total overhead:    {migration_time_ms:.2f} ms ({(migration_time_ms/workload_time_ms)*100:.1f}% of workload)")
    print(f"Pages → Fast tier: {hot_migrated}")
    print(f"Pages → Slow tier: {cold_migrated}")

    return {
        "workload_time_ms": workload_time_ms,
        "migration_time_ms": migration_time_ms,
        "hot_migrated": hot_migrated,
        "cold_migrated": cold_migrated,
        "policy": policy
    }


if __name__ == "__main__":
    # Run with frequency policy
    print("\n>>> Running with FREQUENCY policy...")
    freq_results = run_tiering_system(policy="frequency")

    print("\n>>> Running with LRU policy...")
    lru_results = run_tiering_system(policy="lru")
