import csv
import os

class AccessMonitor:
    """
    Tracks how often each 'page' (fixed-size chunk) of a buffer is accessed.
    Simulates hardware-assisted hot-page detection in software.
    """

    def __init__(self, buffer_size, page_size=4096):
        self.page_size = page_size
        self.num_pages = (buffer_size + page_size - 1) // page_size
        self.access_counts = [0] * self.num_pages

    def record_access(self, address):
        """Call this every time an address is accessed."""
        page_id = address // self.page_size
        self.access_counts[page_id] += 1

    def classify_pages(self, hot_fraction=0.2):
        """
        Returns a list of (page_id, access_count, classification)
        where classification is 'hot' or 'cold'.
        Top `hot_fraction` of pages by access count are marked hot.
        """
        # Pair page_id with its count
        indexed_counts = list(enumerate(self.access_counts))

        # Sort by access count, descending
        sorted_pages = sorted(indexed_counts, key=lambda x: x[1], reverse=True)

        hot_cutoff = int(self.num_pages * hot_fraction)
        hot_page_ids = set(page_id for page_id, _ in sorted_pages[:hot_cutoff])

        results = []
        for page_id, count in indexed_counts:
            classification = "hot" if page_id in hot_page_ids else "cold"
            results.append((page_id, count, classification))

        return results

    def save_results(self, hot_fraction=0.2, output_path="results/monitoring/access_counts.csv"):
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        results = self.classify_pages(hot_fraction)

        with open(output_path, mode="w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["page_id", "access_count", "classification"])
            writer.writerows(results)

        print(f"Monitoring results saved to {output_path}")
        return results
