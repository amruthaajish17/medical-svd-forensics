import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file
from sklearn.metrics import roc_curve, auc

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from block_division import divide_into_blocks
from tampering import (
    apply_pixel_tampering,
    apply_region_tampering,
    apply_copy_move_tampering,
    apply_splicing_tampering,
    apply_inpainting_tampering
)
from ai_tampering import apply_gan_lesion_insertion
from metrics import TamperDetectionMetrics

def run_feature_ablation():
    print("===========================================================================")
    print("DAY 8 EXPERIMENT: SVD FEATURE ABLATION STUDY & ROC-AUC ANALYSIS")
    print("===========================================================================")

    # 1. Load CT Image
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    block_size = 16
    h, w = img_orig.shape

    feats_orig, positions = process_image_to_features(img_orig, block_size)
    df_orig = pd.DataFrame(feats_orig)

    # 2. Build representative test dataset covering all tampering attack families
    test_cases = [
        ("Region Lesion", apply_region_tampering(img_orig, region_size=(20, 20), intensity_delta=0.35)),
        ("Copy-Move", apply_copy_move_tampering(img_orig, patch_size=(24, 24))),
        ("Splicing", apply_splicing_tampering(img_orig, patch_size=(20, 20))),
        ("Inpainting", apply_inpainting_tampering(img_orig, patch_size=(20, 20))),
        ("CT-GAN", apply_gan_lesion_insertion(img_orig, nodule_size=24, intensity=0.38))
    ]

    # Aggregate ground truth labels and feature deltas across all test cases
    y_true_all = []
    feature_deltas = {
        "sigma_1": [],
        "sum_sigma": [],
        "sum_sigma_sq": [],
        "ratio": [],
        "entropy": [],
        "sigma_1 + entropy": [],
        "all_combined": []
    }

    for name, (img_tamp, mask_gt) in test_cases:
        feats_tamp, _ = process_image_to_features(img_tamp, block_size)
        df_tamp = pd.DataFrame(feats_tamp)

        blocks_gt, _ = divide_into_blocks(mask_gt, block_size)
        y_case = [1 if np.mean(b) >= 0.1 else 0 for b in blocks_gt]
        y_true_all.extend(y_case)

        # Compute individual feature deltas
        d_s1 = (df_orig["sigma_1"] - df_tamp["sigma_1"]).abs().values
        d_trace = (df_orig["sum_sigma"] - df_tamp["sum_sigma"]).abs().values
        d_frob = (df_orig["sum_sigma_sq"] - df_tamp["sum_sigma_sq"]).abs().values
        d_ratio = (df_orig["ratio"] - df_tamp["ratio"]).abs().values
        d_ent = (df_orig["entropy"] - df_tamp["entropy"]).abs().values

        feature_deltas["sigma_1"].extend(d_s1)
        feature_deltas["sum_sigma"].extend(d_trace)
        feature_deltas["sum_sigma_sq"].extend(d_frob)
        feature_deltas["ratio"].extend(d_ratio)
        feature_deltas["entropy"].extend(d_ent)

        # Combinations
        norm_s1 = d_s1 / (d_s1.max() + 1e-8)
        norm_ent = d_ent / (d_ent.max() + 1e-8)
        norm_trace = d_trace / (d_trace.max() + 1e-8)
        norm_frob = d_frob / (d_frob.max() + 1e-8)
        norm_ratio = d_ratio / (d_ratio.max() + 1e-8)

        comb_s1_ent = norm_s1 + norm_ent
        comb_all = (norm_s1 + norm_ent + norm_trace + norm_frob + norm_ratio) / 5.0

        feature_deltas["sigma_1 + entropy"].extend(comb_s1_ent)
        feature_deltas["all_combined"].extend(comb_all)

    y_true_arr = np.array(y_true_all)
    print(f"Aggregated {len(y_true_arr)} block samples across 5 tampering families.")
    print(f"Tampered blocks: {np.sum(y_true_arr)}, Authentic blocks: {len(y_true_arr) - np.sum(y_true_arr)}")

    # 3. Compute ROC curves and AUC for each feature
    results = []
    roc_data = {}

    print("\nComputing ROC curves and AUC for individual features & combinations:")
    for feat_name, scores in feature_deltas.items():
        score_arr = np.array(scores)
        # Normalize scores to [0, 1]
        norm_scores = (score_arr - score_arr.min()) / (score_arr.max() - score_arr.min() + 1e-8)

        fpr, tpr, thresholds = roc_curve(y_true_arr, norm_scores)
        feature_auc = auc(fpr, tpr)
        roc_data[feat_name] = (fpr, tpr, feature_auc)

        # Optimal threshold using Youden's J statistic
        j_scores = tpr - fpr
        opt_idx = np.argmax(j_scores)
        opt_thresh = thresholds[opt_idx]

        metrics = TamperDetectionMetrics.calculate_block_level_metrics(y_true_arr, norm_scores, threshold=opt_thresh)

        row = {
            "feature_set": feat_name,
            "auc": feature_auc,
            "optimal_threshold": float(opt_thresh),
            "f1_score": metrics["f1"],
            "accuracy": metrics["accuracy"],
            "precision": metrics["precision"],
            "recall": metrics["recall"],
            "mean_delta": float(score_arr.mean()),
            "std_delta": float(score_arr.std())
        }
        results.append(row)
        print(f"  [{feat_name:<20}] AUC: {feature_auc:.4f} | F1: {metrics['f1']:.4f} | Opt Thresh: {opt_thresh:.4f}")

    results_df = pd.DataFrame(results).sort_values(by="auc", ascending=False)
    csv_path = "results/metrics/day8_feature_ablation_results.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\n[+] Saved ablation results to '{csv_path}'.")

    # 4. Generate Publication-Quality Multi-Panel Figure
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Panel (a): ROC Curves
    palette = {
        "sigma_1": "#1f77b4",
        "sum_sigma": "#ff7f0e",
        "sum_sigma_sq": "#2ca02c",
        "ratio": "#d62728",
        "entropy": "#9467bd",
        "sigma_1 + entropy": "#8c564b",
        "all_combined": "#e377c2"
    }

    for feat_name, (fpr, tpr, f_auc) in roc_data.items():
        linewidth = 3 if feat_name in ["sigma_1 + entropy", "entropy"] else 1.8
        linestyle = "-" if "entropy" in feat_name else "--"
        axes[0].plot(fpr, tpr, label=f"{feat_name} (AUC={f_auc:.3f})", color=palette[feat_name], linewidth=linewidth, linestyle=linestyle)

    axes[0].plot([0, 1], [0, 1], 'k:', alpha=0.6, label="Random Guess (AUC=0.500)")
    axes[0].set_title("(a) Receiver Operating Characteristic (ROC) Comparison", fontweight='bold', fontsize=12)
    axes[0].set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11)
    axes[0].set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11)
    axes[0].set_xlim([0.0, 1.0])
    axes[0].set_ylim([0.0, 1.05])
    axes[0].grid(True, linestyle="--", alpha=0.5)
    axes[0].legend(loc="lower right", fontsize=9.5)

    # Panel (b): AUC Bar Ranking
    bars = axes[1].barh(results_df["feature_set"], results_df["auc"], color="#2b5c8f", edgecolor="black")
    axes[1].set_xlim([0.5, 1.05])
    axes[1].set_xlabel("Area Under the ROC Curve (AUC)", fontsize=11)
    axes[1].set_title("(b) Feature Discriminative Power Ranking (AUC)", fontweight='bold', fontsize=12)
    axes[1].grid(True, linestyle="--", alpha=0.5, axis="x")

    for bar in bars:
        w_val = bar.get_width()
        axes[1].text(w_val + 0.01, bar.get_y() + bar.get_height()/2.0, f"{w_val:.4f}", va='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    fig_path = "figures/day8_roc_curves_ablation.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"[+] Saved ROC ablation curves to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_feature_ablation()
