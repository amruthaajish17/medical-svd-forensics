from pathlib import Path

folders = [
    "data/authentic", "data/tampered", "data/masks",
    "data/m3dsynth/authentic", "data/m3dsynth/manipulated", "data/m3dsynth/masks",
    "src", "experiments",
    "results/features", "results/metrics", "results/anomalies",
    "figures", "paper/sections", "paper/references", "paper/tables",
]
for f in folders:
    Path(f).mkdir(parents=True, exist_ok=True)
print("All folders created.")