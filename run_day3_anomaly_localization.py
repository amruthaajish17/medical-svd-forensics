import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import blocks_to_image
from tampering import apply_region_tampering

def run_anomaly_localization():
    print("===========================================================================")
    print("DAY 3 EXPERIMENT: SVD ANOMALY MAP & TAMPER LOCALIZATION (PERSON A)")
    print("===========================================================================")

    # 1. Load real CT slice
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    print(f"Loaded CT Image Shape: {img_orig.shape}")

    # 2. Apply controlled region tampering (16x16 block lesion insertion)
    block_size = 16
    img_tamp, mask_gt = apply_region_tampering(img_orig, region_size=(16, 16), intensity_delta=0.4)
    print("Applied 16x16 local block tampering to CT slice.")

    # 3. Extract block SVD features
    feats_orig, positions = process_image_to_features(img_orig, block_size)
    feats_tamp, _ = process_image_to_features(img_tamp, block_size)

    df_orig = pd.DataFrame(feats_orig)
    df_tamp = pd.DataFrame(feats_tamp)

    # Calculate SVD Anomaly Map for Entropy & Dominant Singular Value
    delta_entropy = (df_orig["entropy"] - df_tamp["entropy"]).abs().values
    delta_sigma1 = (df_orig["sigma_1"] - df_tamp["sigma_1"]).abs().values

    # Reconstruct 2D Anomaly Heatmaps
    anomaly_map_entropy = blocks_to_image(delta_entropy, positions, img_orig.shape, block_size)
    anomaly_map_sigma1 = blocks_to_image(delta_sigma1, positions, img_orig.shape, block_size)

    np.save("results/anomalies/day3_anomaly_map.npy", anomaly_map_entropy)
    print("[+] Saved 2D anomaly heatmap matrix to 'results/anomalies/day3_anomaly_map.npy'.")

    # 4. Generate Publication-Quality Figure (4 Panels)
    fig, axes = plt.subplots(1, 4, figsize=(20, 5))

    # Panel 1: Original CT
    axes[0].imshow(img_orig, cmap="gray")
    axes[0].set_title("(a) Authentic CT Image", fontsize=12, fontweight='bold')
    axes[0].axis("off")

    # Panel 2: Tampered CT
    axes[1].imshow(img_tamp, cmap="gray")
    axes[1].set_title("(b) Tampered CT Image", fontsize=12, fontweight='bold')
    axes[1].axis("off")

    # Panel 3: Ground Truth Mask
    axes[2].imshow(mask_gt, cmap="binary")
    axes[2].set_title("(c) Ground Truth Mask", fontsize=12, fontweight='bold')
    axes[2].axis("off")

    # Panel 4: SVD Spectral Entropy Anomaly Map
    im = axes[3].imshow(anomaly_map_entropy, cmap="hot")
    axes[3].set_title("(d) SVD Anomaly Map (Localizing)", fontsize=12, fontweight='bold')
    axes[3].axis("off")
    cbar = plt.colorbar(im, ax=axes[3], fraction=0.046, pad=0.04)
    cbar.set_label("Anomaly Magnitude ($\Delta H$)", fontsize=10)

    plt.tight_layout()
    fig_path = "figures/day3_svd_anomaly_map.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"[+] Saved tamper localization figure to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_anomaly_localization()
