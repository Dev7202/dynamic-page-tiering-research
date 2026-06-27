import csv
import matplotlib.pyplot as plt

run_ids = []
times = []

with open("results/baseline/summary.csv", mode="r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        run_ids.append(int(row["run_id"]))
        times.append(float(row["total_time_ms"]))

plt.figure(figsize=(8, 5))
plt.bar(run_ids, times, color="steelblue")
plt.xlabel("Run Number")
plt.ylabel("Total Time (ms)")
plt.title("Baseline Workload Performance (No Tiering)")
plt.xticks(run_ids)
plt.tight_layout()

plt.savefig("results/graphs/baseline_performance.png")
print("Graph saved to results/graphs/baseline_performance.png")
