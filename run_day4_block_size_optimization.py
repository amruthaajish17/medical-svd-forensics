import sys
sys.path.insert(0, 'src')

import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import divide_into_blocks, blocks_to_image
from tampering import apply_region_tampering
from metrics import TamperDetectionMetrics

def run_block_size_optimization():
    print("===========================================================================")
    print("DAY 4 EXPERIMENT: BLOCK SIZE OPTIMIZATION (8x8, 16x16, 32x32)")
    print("===========================================================================")

    # 1. Load test CT slice
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    h, w = img_orig.shape
    print(f"Loaded CT Image: {h}x{w}")

    # 2. Apply controlled 32x32 region tampering
    region_tamper_size = (32, 32)
    img_tamp, mask_gt = apply_region_tampering(
        img_orig, region_size=region_tamper_size, start_pos=(h // 3, w // 3), intensity_delta=0.35
    )

    block_sizes = [8, 16, 32]
    results_list = []

    print("\nEvaluating block size performance and localization precision...")
    for bs in block_sizes:
        start_time = time.perf_counter()

        # Extract features for original and tampered images
        feats_orig, positions = process_image_to_features(img_orig, block_size=bs)
        feats_tamp, _ = process_image_to_features(img_tamp, block_size=bs)

        elapsed_time = time.perf_counter() - start_time

        df_orig = pd.DataFrame(feats_orig)
        df_tamp = pd.DataFrame(feats_tamp)

        # Anomaly score per block = spectral entropy delta + normalized sigma_1 delta
        entropy_delta = (df_orig["entropy"] - df_tamp["entropy"]).abs().values
        sigma1_delta = (df_orig["sigma_1"] - df_tamp["sigma_1"]).abs().values
        anomaly_score = entropy_delta + (sigma1_delta / (sigma1_delta.max() + 1e-8))

        # Ground truth per block: block is tampered if >= 20% of its pixels are in mask_gt
        blocks_gt, _ = divide_into_blocks(mask_gt, block_size=bs)
        y_true = np.array([1 if np.mean(b) >= 0.2 else 0 for b in blocks_gt])

        # Normalize anomaly scores to [0, 1] for classification thresholding
        anomaly_norm = (anomaly_score - anomaly_score.min()) / (anomaly_score.max() - anomaly_score.min() + 1e-8)
        
        # Determine optimal threshold or use 0.25 on min-max normalized delta
        metrics = TamperDetectionMetrics.calculate_block_level_metrics(y_true, anomaly_norm, threshold=0.25)
        auc_score = TamperDetectionMetrics.calculate_roc_auc(y_true, anomaly_norm)

        # Reconstruct predicted binary mask
        pred_blocks_binary = (anomaly_norm >= 0.25).astype(float)
        pred_mask_2d = blocks_to_image(pred_blocks_binary, positions, img_orig.shape, block_size=bs)
        iou_score = TamperDetectionMetrics.calculate_localization_iou(mask_gt, pred_mask_2d)

        row = {
            "block_size": f"{bs}x{bs}",
            "block_dim": bs,
            "num_blocks": len(positions),
            "runtime_ms": elapsed_time * 1000.0,
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "fpr": metrics["fpr"],
            "auc": auc_score,
            "iou": iou_score
        }
        results_list.append(row)

        print(f"  - Block Size: {bs:2d}x{bs:2d} | Blocks: {len(positions):4d} | Runtime: {elapsed_time*1000.0:6.2f} ms | F1: {metrics['f1']:.4f} | IoU: {iou_score:.4f} | AUC: {auc_score:.4f}")

    results_df = pd.DataFrame(results_list)
    out_csv = "results/metrics/day4_block_size_results.csv"
    results_df.to_csv(out_csv, index=False)
    print(f"\n[+] Results saved to '{out_csv}'.")

    # 3. Plot Comparison Charts
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))

    # Metric Bars
    x = np.arange(len(block_sizes))
    width = 0.22
    axes[0].bar(x - width, results_df["precision"], width, label="Precision", color="#2b5c8f")
    axes[0].bar(x, results_df["recall"], width, label="Recall", color="#e27c38")
    axes[0].bar(x + width, results_df["f1"], width, label="F1-Score", color="#2ca02c")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels([f"{b}x{b}" for b in block_sizes], fontsize=11)
    axes[0].set_title("Detection Performance Across Block Sizes", fontweight='bold')
    axes[0].set_ylabel("Score")
    axes[0].set_ylim(0, 1.1)
    axes[0].grid(True, linestyle="--", alpha=0.5, axis="y")
    axes[0].legend()

    # Localization IoU
    axes[1].bar(x, results_df["iou"], width=0.4, color="#9467bd", edgecolor="black")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels([f"{b}x{b}" for b in block_sizes], fontsize=11)
    axes[1].set_title("Spatial Localization IoU by Block Size", fontweight='bold')
    axes[1].set_ylabel("Intersection-over-Union (IoU)")
    axes[1].set_ylim(0, 1.1)
    axes[1].grid(True, linestyle="--", alpha=0.5, axis="y")

    # Computational Runtime
    axes[2].plot([f"{b}x{b}" for b in block_sizes], results_df["runtime_ms"], marker='o', linewidth=2.5, color="#d62728")
    axes[2].set_title("Computation Time per CT Slice (ms)", fontweight='bold')
    axes[2].set_ylabel("Execution Time (milliseconds)")
    axes[2].grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig_path = "figures/day4_block_size_comparison.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"[+] Saved comparative figure to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_block_size_optimization()
