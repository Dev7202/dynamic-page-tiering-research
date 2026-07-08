import ctypes
import ctypes.util
import os
import csv
import time

# Load the C library for move_pages syscall
libc = ctypes.CDLL(ctypes.util.find_library("c"), use_errno=True)

# NUMA node constants — simulating two tiers
FAST_TIER = 0   # simulated "fast" DRAM tier (NUMA node 0)
SLOW_TIER = 1   # simulated "slow" NVM tier (NUMA node 1)

def get_numa_node_count():
    """Check how many NUMA nodes are available on this system."""
    try:
        result = os.popen("numactl --hardware | grep 'available:' | awk '{print $2}'").read().strip()
        return int(result)
    except:
        return 1

def move_page(pid, address, target_node):
    """
    Attempt to move a single page to a target NUMA node.
    Uses move_pages() syscall via libc.
    Returns 0 on success, -1 on failure.
    """
    # move_pages syscall number on x86_64 Linux
    NR_move_pages = 279

    pages = ctypes.c_void_p(address)
    nodes = ctypes.c_int(target_node)
    status = ctypes.c_int(-1)

    ret = libc.syscall(
        NR_move_pages,
        pid,
        1,  # number of pages
        ctypes.byref(pages),
        ctypes.byref(nodes),
        ctypes.byref(status),
        1   # MPOL_MF_MOVE flag
    )

    return ret


class MigrationEngine:
    """
    Simulates page migration between fast (DRAM) and slow (NVM) memory tiers.
    In a single-NUMA-node setup, migration is tracked logically since
    physical movement requires multiple NUMA nodes.
    """

    def __init__(self, page_size=4096):
        self.page_size = page_size
        self.numa_nodes = get_numa_node_count()
        self.migration_log = []  # tracks all migration decisions

        if self.numa_nodes < 2:
            print("[WARNING] Only 1 NUMA node detected.")
            print("[INFO] Running in SIMULATION MODE — migrations tracked logically.")
            self.simulation_mode = True
        else:
            print(f"[INFO] {self.numa_nodes} NUMA nodes detected — physical migration enabled.")
            self.simulation_mode = False

    def migrate_pages(self, classified_pages, buffer_base_address=0):
        """
        Takes classified pages from AccessMonitor and migrates:
        - Hot pages → FAST_TIER (NUMA node 0)
        - Cold pages → SLOW_TIER (NUMA node 1)

        classified_pages: list of (page_id, access_count, classification)
        buffer_base_address: base address of the buffer (0 in simulation mode)
        """
        pid = os.getpid()
        migrated_hot = 0
        migrated_cold = 0
        start_time = time.time()

        for page_id, access_count, classification in classified_pages:
            address = buffer_base_address + (page_id * self.page_size)
            target_node = FAST_TIER if classification == "hot" else SLOW_TIER

            if self.simulation_mode:
                # In simulation mode, just log the decision
                result = "simulated"
            else:
                # Attempt actual physical migration
                ret = move_page(pid, address, target_node)
                result = "success" if ret == 0 else "failed"

            self.migration_log.append({
                "page_id": page_id,
                "access_count": access_count,
                "classification": classification,
                "target_node": target_node,
                "result": result
            })

            if classification == "hot":
                migrated_hot += 1
            else:
                migrated_cold += 1

        end_time = time.time()
        migration_time_ms = (end_time - start_time) * 1000

        print(f"Migration complete in {migration_time_ms:.2f} ms")
        print(f"Hot pages → Fast tier: {migrated_hot}")
        print(f"Cold pages → Slow tier: {migrated_cold}")

        return migration_time_ms, migrated_hot, migrated_cold

    def save_migration_log(self, output_path="results/migration/migration_log.csv"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "page_id", "access_count", "classification", "target_node", "result"
            ])
            writer.writeheader()
            writer.writerows(self.migration_log)

        print(f"Migration log saved to {output_path}")
