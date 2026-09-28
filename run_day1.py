import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Connect to the src folder
sys.path.insert(0, 'src')
# pyrefly: ignore [missing-import]
from block_division import blocks_to_image
# pyrefly: ignore [missing-import]
from svd_features import process_image_to_features

# 1. Generate synthetic host image
print("Processing synthetic image...")
img = np.random.rand(256, 256)

# 2. Extract features
block_size = 16
features, positions = process_image_to_features(img, block_size)

# 3. Export to CSV
df = pd.DataFrame(features)
df["block_x"] = [p[0] for p in positions]
df["block_y"] = [p[1] for p in positions]
df.to_csv("results/features/day1_synthetic_features.csv", index=False)
print(f"Saved {len(df)} rows to results/features/day1_synthetic_features.csv")

# 4. Create and save verification plot
fig, axes = plt.subplots(1, 2, figsize=(10, 4))
axes[0].imshow(img, cmap="gray")
axes[0].set_title("Synthetic Host Image")
axes[0].axis("off")

sigma_1_vals = np.array([f["sigma_1"] for f in features])
heatmap = blocks_to_image(sigma_1_vals, positions, img.shape, block_size)

im = axes[1].imshow(heatmap, cmap="hot")
axes[1].set_title("SVD Sigma_1 Heatmap")
axes[1].axis("off")
plt.colorbar(im, ax=axes[1])

plt.tight_layout()
plt.savefig("figures/day1_svd_pipeline.png", dpi=150)
print("Saved figures/day1_svd_pipeline.png")
print("✅ Day 1 Complete!")