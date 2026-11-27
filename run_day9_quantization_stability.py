import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import hashlib
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from svd_features import process_image_to_features
from tampering import apply_region_tampering
from quantization import quantize_features, serialize_canonical_block

def run_quantization_stability_experiment():
    print("===========================================================================")
    print("DAY 9 EXPERIMENT: CANONICAL FEATURE QUANTIZATION & REPEATABILITY")
    print("===========================================================================")

    # 1. Load real CT scan
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    block_size = 16

    num_runs = 5
    precisions = [2, 3, 4, 5, 6]

    results = []
    print(f"Testing feature repeatability and byte-stability across {num_runs} independent runs...")
    
    img_tamp, _ = apply_region_tampering(img_orig, region_size=(16, 16), intensity_delta=0.35)

    for p in precisions:
        # Check identical deterministic repeatability across runs
        run_hashes = []
        for r in range(num_runs):
            feats, positions = process_image_to_features(img_orig, block_size)
            full_digest = hashlib.sha256()
            for f, (x, y) in zip(feats, positions):
                q = quantize_features(f, precision_decimals=p)
                canonical_bytes = serialize_canonical_block(q, x, y)
                full_digest.update(canonical_bytes)
            run_hashes.append(full_digest.hexdigest())

        # Measure deterministic hash identity
        deterministic_stable = (len(set(run_hashes)) == 1)

        # Check sensitivity to genuine tampering at this precision
        feats_tamp, positions = process_image_to_features(img_tamp, block_size)
        tampered_blocks_detected = 0

        feats_ref, _ = process_image_to_features(img_orig, block_size)
        for f_ref, f_tamp, (x, y) in zip(feats_ref, feats_tamp, positions):
            q_ref = quantize_features(f_ref, precision_decimals=p)
            q_tamp = quantize_features(f_tamp, precision_decimals=p)
            b_ref = serialize_canonical_block(q_ref, x, y)
            b_tamp = serialize_canonical_block(q_tamp, x, y)
            if b_ref != b_tamp:
                tampered_blocks_detected += 1

        row = {
            "decimal_precision": p,
            "scale_factor": 10**p,
            "deterministic_reproducibility": 1.0 if deterministic_stable else 0.0,
            "tampered_blocks_detected": tampered_blocks_detected,
            "quantization_step": 1.0 / (10**p)
        }
        results.append(row)
        print(f"  [Decimals: {p} | Scale: 10^{p}] Deterministic Match: {deterministic_stable} (100%) | Tampered Blocks Flagged: {tampered_blocks_detected}")

    results_df = pd.DataFrame(results)
    csv_path = "results/metrics/day9_quantization_stability.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\n[+] Saved quantization stability metrics to '{csv_path}'.")

    # 3. Plot Quantization Optimization Trade-off
    fig, ax1 = plt.subplots(figsize=(10, 5))

    color = '#1f77b4'
    ax1.set_xlabel('Quantization Decimal Precision ($d$)', fontsize=11)
    ax1.set_ylabel('Deterministic Hash Match (%)', color=color, fontsize=11)
    ax1.plot(results_df["decimal_precision"], results_df["deterministic_reproducibility"] * 100, marker='s', linewidth=2.5, color=color, label="Reproducibility")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylim([0, 110])
    ax1.grid(True, linestyle="--", alpha=0.5)

    ax2 = ax1.twinx()
    color = '#d62728'
    ax2.set_ylabel('Tampered Blocks Flagged ($N$)', color=color, fontsize=11)
    ax2.plot(results_df["decimal_precision"], results_df["tampered_blocks_detected"], marker='o', linewidth=2.5, color=color, linestyle="--", label="Tamper Sensitivity")
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim([0, max(results_df["tampered_blocks_detected"]) + 2])

    plt.title("Deterministic Feature Quantization: Reproducibility & Tamper Sensitivity", fontweight='bold', fontsize=12)
    fig.tight_layout()
    fig_path = "figures/day9_quantization_stability.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"[+] Saved quantization figure to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_quantization_stability_experiment()
