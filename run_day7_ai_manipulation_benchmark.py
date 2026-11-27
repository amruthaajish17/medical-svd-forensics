import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file
from pathlib import Path
import cv2

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import divide_into_blocks, blocks_to_image
from ai_tampering import (
    apply_gan_lesion_insertion,
    apply_diffusion_inpainting,
    setup_m3dsynth_dataset_hierarchy
)
from metrics import TamperDetectionMetrics

def run_ai_manipulation_benchmark():
    print("===========================================================================")
    print("DAY 7 EXPERIMENT: AI-GENERATED (GAN & DIFFUSION) MANIPULATION BENCHMARK")
    print("===========================================================================")

    setup_m3dsynth_dataset_hierarchy()

    # 1. Load real CT scan
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    h, w = img_orig.shape
    block_size = 16
    print(f"Loaded CT Image: {h}x{w}, Block size: {block_size}x{block_size}")

    # Baseline authentic features
    feats_orig, positions = process_image_to_features(img_orig, block_size)
    df_orig = pd.DataFrame(feats_orig)

    # 2. Generate modern AI manipulations
    # Attack 1: GAN-generated lung nodule insertion (CT-GAN simulation)
    img_gan, mask_gan = apply_gan_lesion_insertion(img_orig, nodule_size=24, position=(int(h*0.4), int(w*0.48)), intensity=0.38, seed=42)

    # Attack 2: Diffusion model semantic inpainting (MedDDPM tissue reconstruction)
    img_diff, mask_diff = apply_diffusion_inpainting(img_orig, inpaint_size=26, position=(int(h*0.32), int(w*0.32)), seed=42)

    # Save to data/m3dsynth hierarchy
    cv2.imwrite("data/m3dsynth/authentic/ct_orig.png", (img_orig * 255).astype(np.uint8))
    cv2.imwrite("data/m3dsynth/manipulated/ct_gan_nodule.png", (img_gan * 255).astype(np.uint8))
    cv2.imwrite("data/m3dsynth/masks/ct_gan_mask.png", (mask_gan * 255).astype(np.uint8))
    cv2.imwrite("data/m3dsynth/manipulated/ct_diff_inpaint.png", (img_diff * 255).astype(np.uint8))
    cv2.imwrite("data/m3dsynth/masks/ct_diff_mask.png", (mask_diff * 255).astype(np.uint8))
    print("[+] Archived paired datasets into data/m3dsynth/ directory.")

    ai_attacks = {
        "GAN Lesion Insertion (CT-GAN)": (img_gan, mask_gan),
        "Diffusion Inpainting (MedDDPM)": (img_diff, mask_diff)
    }

    results = []
    anomaly_heatmaps = {}

    fig, axes = plt.subplots(2, 4, figsize=(18, 9))

    for idx, (model_name, (img_tamp, mask_gt)) in enumerate(ai_attacks.items()):
        feats_tamp, _ = process_image_to_features(img_tamp, block_size)
        df_tamp = pd.DataFrame(feats_tamp)

        delta_entropy = (df_orig["entropy"] - df_tamp["entropy"]).abs().values
        delta_sigma1 = (df_orig["sigma_1"] - df_tamp["sigma_1"]).abs().values
        anomaly_score = delta_entropy + (delta_sigma1 / (delta_sigma1.max() + 1e-8))

        anomaly_map = blocks_to_image(anomaly_score, positions, img_orig.shape, block_size)
        anomaly_heatmaps[model_name] = anomaly_map

        blocks_gt, _ = divide_into_blocks(mask_gt, block_size)
        y_true = np.array([1 if np.mean(b) >= 0.1 else 0 for b in blocks_gt])

        anomaly_norm = (anomaly_score - anomaly_score.min()) / (anomaly_score.max() - anomaly_score.min() + 1e-8)
        thresh = 0.20
        metrics = TamperDetectionMetrics.calculate_block_level_metrics(y_true, anomaly_norm, threshold=thresh)
        auc_score = TamperDetectionMetrics.calculate_roc_auc(y_true, anomaly_norm)

        pred_mask_2d = blocks_to_image((anomaly_norm >= thresh).astype(float), positions, img_orig.shape, block_size)
        iou_score = TamperDetectionMetrics.calculate_localization_iou(mask_gt, pred_mask_2d)

        row = {
            "ai_manipulation_model": model_name,
            "modified_pixels": int(mask_gt.sum()),
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

        print(f"  [{model_name}] F1: {metrics['f1']:.4f} | IoU: {iou_score:.4f} | AUC: {auc_score:.4f} | Max Delta H: {delta_entropy.max():.4f}")

        # Render 4 panels
        axes[idx, 0].imshow(img_orig, cmap="gray")
        axes[idx, 0].set_title("Authentic Host CT", fontsize=11)
        axes[idx, 0].axis("off")

        axes[idx, 1].imshow(img_tamp, cmap="gray")
        axes[idx, 1].set_title(f"Manipulated: {model_name}", fontsize=11, fontweight="bold")
        axes[idx, 1].axis("off")

        axes[idx, 2].imshow(mask_gt, cmap="binary")
        axes[idx, 2].set_title("Ground Truth Mask", fontsize=11)
        axes[idx, 2].axis("off")

        im = axes[idx, 3].imshow(anomaly_map, cmap="hot")
        axes[idx, 3].set_title(f"SVD Anomaly Map (F1: {metrics['f1']:.2f}, AUC: {auc_score:.2f})", fontsize=11)
        axes[idx, 3].axis("off")
        plt.colorbar(im, ax=axes[idx, 3], fraction=0.046, pad=0.04)

    plt.tight_layout()
    fig_path = "figures/day7_ai_manipulation_detection.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"\n[+] Saved AI manipulation figure to '{fig_path}'.")

    results_df = pd.DataFrame(results)
    csv_path = "results/metrics/day7_ai_manipulation_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"[+] Saved AI manipulation metrics to '{csv_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_ai_manipulation_benchmark()
