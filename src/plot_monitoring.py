import csv
import matplotlib.pyplot as plt

page_ids = []
counts = []
colors = []

with open("results/monitoring/access_counts.csv", mode="r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        page_ids.append(int(row["page_id"]))
        counts.append(int(row["access_count"]))
        colors.append("crimson" if row["classification"] == "hot" else "steelblue")

plt.figure(figsize=(12, 5))
plt.bar(page_ids, counts, color=colors, width=1.0)
plt.xlabel("Page ID")
plt.ylabel("Access Count")
plt.title("Page Access Distribution (Red = Hot, Blue = Cold)")
plt.tight_layout()

plt.savefig("results/graphs/access_distribution.png")
print("Graph saved to results/graphs/access_distribution.png")
