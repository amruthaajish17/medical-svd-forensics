# 14-Day Medical SVD Forensics & Cryptographic Authentication: Daily Progress Guide

This document provides a day-by-day, easy-to-understand breakdown of the entire research project: **"Passive SVD-Based Medical CT Tamper Forensics and Lightweight Cryptographic Spatial Authentication"**.

---

## 📅 Roadmap Overview (2-Week Intensive Execution)

| Day | Focus Area | Key Objectives | Status |
|---|---|---|---|
| **Day 1** | Mathematical Core | DICOM Loading, Block Division, 5 SVD Feature Extractors | ✅ Completed |
| **Day 2** | Sensitivity Analysis | Micro-scale pixel modifications (1 to 100 px), Feature sensitivity curve | ✅ Completed |
| **Day 3** | Anomaly Mapping | 2D difference heatmaps, spatial lesion localization | ✅ Completed |
| **Day 4** | Block Size Optimization | Evaluating 8×8, 16×16, 32×32 block trade-offs, Full metrics suite (F1, IoU, AUC) | ✅ Completed |
| **Day 5** | Multi-Attack Forensics | Copy-move, splicing, and inpainting attack simulation & detection | 🔄 In Progress |
| **Day 6** | Benign Transformation Robustness | Testing Gaussian noise, blur, compression to suppress false alarms | ⏳ Pending |
| **Day 7** | AI & Deepfake Inpainting | Simulating generative AI lesion insertions (M3Dsynth framework) | ⏳ Pending |
| **Day 8** | Feature Ablation & ROC Analysis | Finding dominant singular features vs. spectral entropy via ROC-AUC | ⏳ Pending |
| **Day 9** | Canonical Quantization | Floating-point quantization & deterministic serialization for crypto | ⏳ Pending |
| **Day 10** | Cryptographic Authentication | Block-level HMAC-SHA256 spatial binding | ⏳ Pending |
| **Day 11** | Merkle Tree Architecture | Hierarchical Merkle tree root verification & leaf-level tamper tracing | ⏳ Pending |
| **Day 12** | Adversarial Threat Modeling | Testing malicious pixel-only, metadata, and key tampering attacks | ⏳ Pending |
| **Day 13** | Publication Assets | Generating high-resolution Figures 1–5 and Tables 1–5 | ⏳ Pending |
| **Day 14** | Manuscript & Master Suite | Complete conference paper manuscript & master execution suite | ⏳ Pending |

---

## 🔍 Detailed Day-by-Day Log Explained Simply

### Day 1: Project Setup, DICOM CT Ingestion & SVD Pipeline
- **What was done in simple terms:**
  We built the bedrock of the project. A medical CT scan is essentially a 2D grid of numbers representing tissue densities (Hounsfield units). We loaded raw DICOM slices, normalized their intensities to the range $[0, 1]$, and cut the image into non-overlapping blocks ($16 \times 16$). For each block, we computed the Singular Value Decomposition (SVD):
  $$B_k = U_k \Sigma_k V_k^T$$
  From the singular values $\Sigma_k = \text{diag}(\sigma_1, \sigma_2, \dots)$, we extracted five intrinsic mathematical properties:
  1. $\sigma_1$: The dominant singular value (captures the principal energy).
  2. $\sum \sigma_i$: Total nuclear norm (trace / overall luminance).
  3. $\sum \sigma_i^2$: Frobenius energy (structural variance).
  4. $\sigma_1 / \sigma_2$: Dominant-to-subdominant energy ratio.
  5. $H = -\sum p_i \log_2(p_i)$: Spectral entropy (measures how ordered or chaotic the block textures are).
- **Key Output Files:**
  - `src/preprocessing.py`, `src/block_division.py`, `src/svd_features.py`
  - `results/features/day1_real_ct_features.csv`
  - `figures/day1_real_ct.png`, `figures/day1_svd_pipeline.png`

---

### Day 2: SVD Feature Sensitivity Sweep (Micro-Tampering)
- **What was done in simple terms:**
  We answered the fundamental question: *Does changing even a few pixels in a medical scan alter its singular value spectrum?* We injected tiny controlled manipulations (modifying 1, 5, 10, 25, and 100 pixels in the central tissue area) and tracked the change $\Delta F = |F_{\text{original}} - F_{\text{tampered}}|$.
- **Key Finding:**
  Both dominant singular value ($\sigma_1$) and spectral entropy ($H$) respond with monotonic increases to tampering, proving that SVD features provide a sensitive signature even when subtle pixel alterations occur.
- **Key Output Files:**
  - `src/tampering.py`
  - `run_day2_sensitivity_experiment.py`
  - `results/metrics/day2_sensitivity_results.csv`
  - `figures/day2_feature_sensitivity.png`

---

### Day 3: Tamper Localization & SVD Anomaly Mapping
- **What was done in simple terms:**
  Detecting that an image was altered is good, but doctors need to know *where* it was altered. We simulated a $16 \times 16$ block lesion insertion and reconstructed a 2D spatial anomaly heatmap:
  $$A_k = |F_k - F'_k|$$
  This heatmap visually pinpointed the exact manipulated region with pinpoint accuracy, matching the ground-truth mask.
- **Key Output Files:**
  - `run_day3_anomaly_localization.py`
  - `results/anomalies/day3_anomaly_map.npy`
  - `figures/day3_svd_anomaly_map.png`

---

### Day 4: Block Size Optimization & Evaluation Metrics
- **What was done in simple terms:**
  We investigated the best block resolution for analyzing CT scans. If blocks are too small ($8 \times 8$), processing takes twice as long ($29\text{ ms}$) and becomes sensitive to noise; if blocks are too large ($32 \times 32$), spatial localization becomes coarse (IoU drops to $0.29$). We benchmarked $8 \times 8$, $16 \times 16$, and $32 \times 32$ across Accuracy, Precision, Recall, F1, and IoU.
- **Key Finding:**
  $16 \times 16$ is optimal. It achieved $F_1 = 1.00$, $\text{AUC} = 1.00$, and an execution time of only $13.38\text{ ms}$ per slice.
- **Key Output Files:**
  - `src/metrics.py`
  - `run_day4_block_size_optimization.py`
  - `results/metrics/day4_block_size_results.csv`
  - `figures/day4_block_size_comparison.png`
