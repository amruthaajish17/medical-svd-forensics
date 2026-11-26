import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import divide_into_blocks
from tampering import apply_region_tampering
from robustness import (
    apply_gaussian_noise,
    apply_jpeg_compression,
    apply_gaussian_blur,
    apply_intensity_drift
)
from metrics import TamperDetectionMetrics

def run_robustness_benchmark():
    print("===========================================================================")
    print("DAY 6 EXPERIMENT: BENIGN CLINICAL DEGRADATIONS & FALSE ALARM RESISTANCE")
    print("===========================================================================")

    # 1. Load real CT scan
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    block_size = 16

    # Baseline authentic features
    feats_orig, positions = process_image_to_features(img_orig, block_size)
    df_orig = pd.DataFrame(feats_orig)

    # 2. Reference genuine malicious attack for comparison (16x16 lesion)
    img_malicious, mask_malicious = apply_region_tampering(img_orig, region_size=(16, 16), intensity_delta=0.35)
    feats_malicious, _ = process_image_to_features(img_malicious, block_size)
    df_malicious = pd.DataFrame(feats_malicious)

    # Calculate malicious anomaly scores
    delta_entropy_mal = (df_orig["entropy"] - df_malicious["entropy"]).abs().values
    delta_sigma1_mal = (df_orig["sigma_1"] - df_malicious["sigma_1"]).abs().values
    anomaly_mal = delta_entropy_mal + (delta_sigma1_mal / (delta_sigma1_mal.max() + 1e-8))

    # 3. Benign transformations
    benign_transforms = {
        "Gaussian Sensor Noise (var=0.0005)": apply_gaussian_noise(img_orig, var=0.0005),
        "PACS JPEG Compression (Q=85)": apply_jpeg_compression(img_orig, quality=85),
        "PACS JPEG Compression (Q=70)": apply_jpeg_compression(img_orig, quality=70),
        "Micro-Motion Blur (k=3, s=0.7)": apply_gaussian_blur(img_orig, kernel_size=(3, 3), sigma=0.7),
        "Intensity Drift (+2%)": apply_intensity_drift(img_orig, delta=0.02),
    }

    # Anomaly threshold defined from Days 4-5 calibration
    detection_threshold = 0.20

    results = []
    all_scores = {"Malicious Tampering": anomaly_mal}

    print("\nEvaluating benign modifications vs Malicious Tamper Threshold...")
    for name, transformed_img in benign_transforms.items():
        feats_benign, _ = process_image_to_features(transformed_img, block_size)
        df_benign = pd.DataFrame(feats_benign)

        delta_entropy = (df_orig["entropy"] - df_benign["entropy"]).abs().values
        delta_sigma1 = (df_orig["sigma_1"] - df_benign["sigma_1"]).abs().values
        anomaly_score = delta_entropy + (delta_sigma1 / (delta_sigma1_mal.max() + 1e-8))

        all_scores[name] = anomaly_score

        # Min-max normalize against the malicious scale
        norm_score = anomaly_score / (anomaly_mal.max() + 1e-8)

        # Ground truth for benign is all 0s (no tampering)
        y_true = np.zeros(len(anomaly_score), dtype=int)
        y_pred = (norm_score >= detection_threshold).astype(int)

        false_alarms = int(y_pred.sum())
        fpr = false_alarms / len(y_true)

        row = {
            "transformation": name,
            "mean_anomaly": float(anomaly_score.mean()),
            "max_anomaly": float(anomaly_score.max()),
            "normalized_max": float(norm_score.max()),
            "false_alarms": false_alarms,
            "total_blocks": len(y_true),
            "false_positive_rate": fpr,
            "passes_benign_filter": bool(false_alarms == 0)
        }
        results.append(row)

        print(f"  [{name:<32}] Max Anom: {norm_score.max():.4f} | False Alarms: {false_alarms:2d}/{len(y_true)} | FPR: {fpr*100:4.1f}%")

    results_df = pd.DataFrame(results)
    csv_path = "results/metrics/day6_robustness_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\n[+] Saved robustness results to '{csv_path}'.")

    # 4. Plot Multi-Panel Scientific Distribution Figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Panel (a): Boxplot of Anomaly Distributions
    labels = list(all_scores.keys())
    data = [all_scores[k] for k in labels]
    bp = axes[0].boxplot(data, tick_labels=[l.split('(')[0].strip() for l in labels], patch_artist=True)
    colors = ['#d62728', '#1f77b4', '#2ca02c', '#ff7f0e', '#9467bd', '#8c564b']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)
    axes[0].axhline(detection_threshold * anomaly_mal.max(), color='black', linestyle='--', linewidth=2, label="Tamper Threshold")
    axes[0].set_title("(a) Anomaly Magnitude Distribution: Malicious vs Benign", fontweight='bold', fontsize=12)
    axes[0].set_ylabel("SVD Spectral Anomaly Score", fontsize=11)
    axes[0].tick_params(axis='x', rotation=30)
    axes[0].legend(loc="upper right")
    axes[0].grid(True, linestyle="--", alpha=0.5, axis="y")

    # Panel (b): Bar chart of False Positive Rate (%)
    axes[1].bar([r["transformation"].split('(')[0].strip() for r in results], results_df["false_positive_rate"] * 100, color="#1f77b4", edgecolor="black")
    axes[1].set_title("(b) False Positive Rate (%) Under Harmless Degradation", fontweight='bold', fontsize=12)
    axes[1].set_ylabel("False Positive Rate (%)", fontsize=11)
    axes[1].set_ylim(0, 10)
    axes[1].axhline(0, color='gray', linewidth=1)
    axes[1].tick_params(axis='x', rotation=30)
    axes[1].grid(True, linestyle="--", alpha=0.5, axis="y")

    plt.tight_layout()
    fig_path = "figures/day6_robustness_analysis.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"[+] Saved robustness figure to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_robustness_benchmark()
