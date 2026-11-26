import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import divide_into_blocks, blocks_to_image
from tampering import (
    apply_pixel_tampering,
    apply_region_tampering,
    apply_copy_move_tampering,
    apply_splicing_tampering,
    apply_inpainting_tampering
)
from metrics import TamperDetectionMetrics

def run_multi_attack_benchmark():
    print("===========================================================================")
    print("DAY 5 EXPERIMENT: MULTI-ATTACK FORENSICS EVALUATION")
    print("===========================================================================")

    # 1. Load real CT scan
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    h, w = img_orig.shape
    block_size = 16
    print(f"Loaded CT Image: {h}x{w}, Block size: {block_size}x{block_size}")

    # Extract authentic baseline features
    feats_orig, positions = process_image_to_features(img_orig, block_size)
    df_orig = pd.DataFrame(feats_orig)

    # 2. Define the attack catalog
    attacks = {
        "Micro-Pixel (10 px)": apply_pixel_tampering(img_orig, num_pixels=10, intensity_delta=0.6),
        "Region Insertion": apply_region_tampering(img_orig, region_size=(20, 20), intensity_delta=0.35),
        "Copy-Move Cloning": apply_copy_move_tampering(img_orig, patch_size=(24, 24)),
        "Splicing (Implant)": apply_splicing_tampering(img_orig, patch_size=(20, 20), intensity_shift=0.4),
        "Inpainting (Removal)": apply_inpainting_tampering(img_orig, patch_size=(20, 20))
    }

    results = []
    anomaly_maps = {}
    attack_images = {}
    ground_truth_masks = {}

    fig, axes = plt.subplots(len(attacks), 4, figsize=(18, 4 * len(attacks)))

    for idx, (attack_name, (img_tamp, mask_gt)) in enumerate(attacks.items()):
        # Extract features for tampered image
        feats_tamp, _ = process_image_to_features(img_tamp, block_size)
        df_tamp = pd.DataFrame(feats_tamp)

        # Anomaly vector per block (Entropy delta + Sigma_1 delta)
        delta_entropy = (df_orig["entropy"] - df_tamp["entropy"]).abs().values
        delta_sigma1 = (df_orig["sigma_1"] - df_tamp["sigma_1"]).abs().values
        anomaly_score = delta_entropy + (delta_sigma1 / (delta_sigma1.max() + 1e-8))

        # Reconstruct 2D Anomaly Heatmap
        anomaly_map = blocks_to_image(anomaly_score, positions, img_orig.shape, block_size)
        anomaly_maps[attack_name] = anomaly_map
        attack_images[attack_name] = img_tamp
        ground_truth_masks[attack_name] = mask_gt

        # Calculate block-level labels & metrics
        blocks_gt, _ = divide_into_blocks(mask_gt, block_size)
        y_true = np.array([1 if np.mean(b) >= 0.1 else 0 for b in blocks_gt])
        
        # Min-max normalization for thresholding
        anomaly_norm = (anomaly_score - anomaly_score.min()) / (anomaly_score.max() - anomaly_score.min() + 1e-8)
        
        # Adaptive threshold based on authentic noise floor
        thresh = 0.20
        metrics = TamperDetectionMetrics.calculate_block_level_metrics(y_true, anomaly_norm, threshold=thresh)
        auc_score = TamperDetectionMetrics.calculate_roc_auc(y_true, anomaly_norm)

        pred_mask_2d = blocks_to_image((anomaly_norm >= thresh).astype(float), positions, img_orig.shape, block_size)
        iou_score = TamperDetectionMetrics.calculate_localization_iou(mask_gt, pred_mask_2d)

        row = {
            "attack_type": attack_name,
            "modified_area_px": int(mask_gt.sum()),
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "f1": metrics["f1"],
            "fpr": metrics["fpr"],
            "auc": auc_score,
            "iou": iou_score,
            "max_delta_entropy": float(delta_entropy.max()),
            "max_delta_sigma1": float(delta_sigma1.max())
        }
        results.append(row)

        print(f"[{attack_name:<20}] F1: {metrics['f1']:.4f} | IoU: {iou_score:.4f} | AUC: {auc_score:.4f} | Max Delta H: {delta_entropy.max():.4f}")

        # Plot 4 panels per attack
        axes[idx, 0].imshow(img_orig, cmap="gray")
        axes[idx, 0].set_title(f"Authentic CT", fontsize=11)
        axes[idx, 0].axis("off")

        axes[idx, 1].imshow(img_tamp, cmap="gray")
        axes[idx, 1].set_title(f"Tampered: {attack_name}", fontsize=11, fontweight="bold")
        axes[idx, 1].axis("off")

        axes[idx, 2].imshow(mask_gt, cmap="binary")
        axes[idx, 2].set_title(f"Ground Truth Mask", fontsize=11)
        axes[idx, 2].axis("off")

        im = axes[idx, 3].imshow(anomaly_map, cmap="hot")
        axes[idx, 3].set_title(f"SVD Anomaly Map (F1: {metrics['f1']:.2f})", fontsize=11)
        axes[idx, 3].axis("off")
        plt.colorbar(im, ax=axes[idx, 3], fraction=0.046, pad=0.04)

    plt.tight_layout()
    fig_path = "figures/day5_multi_attack_detection.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"\n[+] Saved multi-attack visualization figure to '{fig_path}'.")

    results_df = pd.DataFrame(results)
    csv_path = "results/metrics/day5_multi_attack_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"[+] Saved multi-attack metrics to '{csv_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_multi_attack_benchmark()
