import csv
import os

class TieringPolicy:
    """
    Implements two tiering policies:
    1. Frequency-based: classify pages by raw access count (top X% = hot)
    2. LRU-based: classify pages by recency of last access
    """

    def __init__(self, policy="frequency", hot_fraction=0.2, hot_threshold=None):
        """
        policy: "frequency" or "lru"
        hot_fraction: top fraction of pages to classify as hot (default 20%)
        hot_threshold: optional fixed count threshold (frequency policy only)
        """
        self.policy = policy
        self.hot_fraction = hot_fraction
        self.hot_threshold = hot_threshold
        self.last_access_time = {}  # for LRU tracking: page_id -> last access timestamp

    def record_access(self, page_id, timestamp):
        """Record when a page was last accessed (used by LRU policy)."""
        self.last_access_time[page_id] = timestamp

    def classify_frequency(self, access_counts):
        """
        Frequency policy: classify top hot_fraction pages by access count as hot.
        access_counts: list of (page_id, access_count)
        Returns: list of (page_id, access_count, classification)
        """
        sorted_pages = sorted(access_counts, key=lambda x: x[1], reverse=True)
        hot_cutoff = int(len(sorted_pages) * self.hot_fraction)

        if self.hot_threshold is not None:
            # Use fixed threshold if provided
            results = [
                (page_id, count, "hot" if count >= self.hot_threshold else "cold")
                for page_id, count in access_counts
            ]
        else:
            # Use top fraction
            hot_ids = set(page_id for page_id, _ in sorted_pages[:hot_cutoff])
            results = [
                (page_id, count, "hot" if page_id in hot_ids else "cold")
                for page_id, count in access_counts
            ]

        hot_count = sum(1 for _, _, c in results if c == "hot")
        cold_count = sum(1 for _, _, c in results if c == "cold")
        print(f"[Frequency Policy] Hot: {hot_count} pages | Cold: {cold_count} pages")
        return results

    def classify_lru(self, access_counts, current_time):
        """
        LRU policy: pages not accessed recently are classified as cold.
        Pages accessed in the most recent hot_fraction of the time window = hot.
        access_counts: list of (page_id, access_count)
        current_time: current timestamp for recency comparison
        """
        if not self.last_access_time:
            print("[LRU Policy] No access time data — falling back to frequency policy")
            return self.classify_frequency(access_counts)

        # Find recency threshold
        all_times = list(self.last_access_time.values())
        all_times.sort(reverse=True)
        cutoff_index = int(len(all_times) * self.hot_fraction)
        recency_threshold = all_times[cutoff_index] if cutoff_index < len(all_times) else 0

        access_dict = dict(access_counts)
        results = []
        for page_id, count in access_counts:
            last_access = self.last_access_time.get(page_id, 0)
            classification = "hot" if last_access >= recency_threshold else "cold"
            results.append((page_id, count, classification))

        hot_count = sum(1 for _, _, c in results if c == "hot")
        cold_count = sum(1 for _, _, c in results if c == "cold")
        print(f"[LRU Policy] Hot: {hot_count} pages | Cold: {cold_count} pages")
        return results

    def classify(self, access_counts, current_time=None):
        """Main entry point — runs whichever policy is configured."""
        if self.policy == "frequency":
            return self.classify_frequency(access_counts)
        elif self.policy == "lru":
            return self.classify_lru(access_counts, current_time)
        else:
            raise ValueError(f"Unknown policy: {self.policy}")

    def save_policy_results(self, results, output_path="results/policy/policy_results.csv"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["page_id", "access_count", "classification"])
            writer.writerows(results)

        print(f"Policy results saved to {output_path}")
