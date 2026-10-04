import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from tampering import apply_pixel_tampering

def run_sensitivity_experiment():
    print("===========================================================================")
    print("DAY 2 EXPERIMENT: SVD FEATURE SENSITIVITY TO PIXEL TAMPERING (PERSON A)")
    print("===========================================================================")

    # 1. Load real CT slice
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    print(f"Loaded CT Image Shape: {img_orig.shape}")

    # 2. Extract baseline original features
    block_size = 16
    feats_orig, positions = process_image_to_features(img_orig, block_size)
    df_orig = pd.DataFrame(feats_orig)

    pixel_scales = [1, 5, 10, 25, 100]
    feature_keys = ["sigma_1", "sum_sigma", "sum_sigma_sq", "ratio", "entropy"]

    results_list = []

    print("\nRunning tampering sensitivity sweeps across pixel scales...")
    for n_pix in pixel_scales:
        img_tamp, mask = apply_pixel_tampering(img_orig, num_pixels=n_pix, intensity_delta=0.5, seed=42)
        feats_tamp, _ = process_image_to_features(img_tamp, block_size)
        df_tamp = pd.DataFrame(feats_tamp)

        row_data = {"num_pixels_modified": n_pix}

        for key in feature_keys:
            delta_f = (df_orig[key] - df_tamp[key]).abs()
            row_data[f"{key}_mean_delta"] = delta_f.mean()
            row_data[f"{key}_max_delta"] = delta_f.max()
            row_data[f"{key}_total_delta"] = delta_f.sum()

        results_list.append(row_data)
        print(f"  - Pixels modified: {n_pix:<3} | Max Delta Sigma_1: {row_data['sigma_1_max_delta']:.4f} | Max Delta Entropy: {row_data['entropy_max_delta']:.4f}")

    results_df = pd.DataFrame(results_list)
    results_path = "results/metrics/day2_sensitivity_results.csv"
    results_df.to_csv(results_path, index=False)
    print(f"\n[+] Saved sensitivity experiment results to '{results_path}'.")

    # 3. Plot Scientific Sensitivity Graph
    plt.figure(figsize=(10, 6))
    for key in feature_keys:
        plt.plot(results_df["num_pixels_modified"], results_df[f"{key}_max_delta"], marker='o', linewidth=2, label=key)

    plt.title("SVD Feature Response to Local Pixel Tampering (Max $\Delta F$)", fontsize=13, fontweight='bold')
    plt.xlabel("Number of Modified Pixels", fontsize=11)
    plt.ylabel("Maximum Feature Response ($\Delta F = |F_{orig} - F_{tamp}|$)", fontsize=11)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=10)
    plt.tight_layout()

    fig_path = "figures/day2_feature_sensitivity.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"[+] Saved sensitivity graph to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_sensitivity_experiment()
