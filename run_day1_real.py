import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import blocks_to_image

# 1. Real CT slice that ships with pydicom
path = get_testdata_file("CT_small.dcm")
img = load_dicom(path)
print("Loaded:", img.shape, "raw range:", img.min(), "to", img.max())

# 2. Normalize to 0-1
img = normalize_image(img)

# 3. Blocks -> SVD -> features
block_size = 16
features, positions = process_image_to_features(img, block_size)
df = pd.DataFrame(features)
df["block_x"] = [p[0] for p in positions]
df["block_y"] = [p[1] for p in positions]
df.to_csv("results/features/day1_real_ct_features.csv", index=False)
print("Blocks:", len(df))
print(df.describe())

# 4. Plot the image next to three feature maps
names = ["sigma_1", "ratio", "entropy"]
fig, axes = plt.subplots(1, 4, figsize=(18, 4))
axes[0].imshow(img, cmap="gray"); axes[0].set_title("Real CT slice")
for ax, n in zip(axes[1:], names):
    vals = np.array([f[n] for f in features])
    m = blocks_to_image(vals, positions, img.shape, block_size)
    im = ax.imshow(m, cmap="hot"); ax.set_title(n)
    plt.colorbar(im, ax=ax)
for ax in axes: ax.axis("off")
plt.tight_layout()
plt.savefig("figures/day1_real_ct.png", dpi=150, bbox_inches="tight")
print("Saved figures/day1_real_ct.png")