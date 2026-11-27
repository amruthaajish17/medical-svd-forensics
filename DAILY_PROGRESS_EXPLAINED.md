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
| **Day 5** | Multi-Attack Forensics | Copy-move, splicing, and inpainting attack simulation & detection | ✅ Completed |
| **Day 6** | Benign Transformation Robustness | Testing Gaussian noise, blur, compression to suppress false alarms | ✅ Completed |
| **Day 7** | AI & Deepfake Inpainting | Simulating generative AI lesion insertions (M3Dsynth framework) | ✅ Completed |
| **Day 8** | Feature Ablation & ROC Analysis | Finding dominant singular features vs. spectral entropy via ROC-AUC | ✅ Completed |
| **Day 9** | Canonical Quantization | Floating-point quantization & deterministic serialization for crypto | 🔄 In Progress |
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

---

### Day 5: Multi-Attack Forensics Evaluation
- **What was done in simple terms:**
  Attackers don't just change single pixels; they perform sophisticated forgeries:
  1. **Region Tampering**: Inserting a bright lesion or artificial nodule into healthy tissue.
  2. **Copy-Move Forgery**: Duplicating genuine lung tissue or an existing tumor from one part of the scan to another.
  3. **Splicing Attack**: Implanting foreign pathology from another patient's scan into the target scan.
  4. **Inpainting / Lesion Removal**: Erasing a malignant tumor and mathematically smoothing over it to falsely make a patient look healthy.
  We implemented all four attack modalities in `src/tampering.py` and benchmarked SVD anomaly detection against each.
- **Key Finding:**
  The passive SVD detector achieved **$F_1 = 1.00$** on Region Insertion, Splicing, and Inpainting, and **$F_1 = 0.86$** on Copy-Move cloning with perfect $\text{AUC} = 1.00$. This confirms that local SVD spectral characteristics provide a powerful defense against real-world clinical CT falsifications.
- **Key Output Files:**
  - `src/tampering.py` (enhanced multi-attack generator)
  - `run_day5_multi_attack_benchmark.py`
  - `results/metrics/day5_multi_attack_results.csv`
  - `figures/day5_multi_attack_detection.png`

---

### Day 6: Benign Transformations & False Alarm Resistance
- **What was done in simple terms:**
  A forensic detector is useless in a hospital if it triggers on normal, harmless events—like slight camera noise, image compression when sending a file across PACS, or slight patient movement. We subjected genuine CT images to:
  1. Low-dose Gaussian sensor noise
  2. Lossy PACS JPEG compression (Qualities 85 and 70)
  3. Micro-motion blur
  4. Global exposure / calibration intensity drift
- **Key Finding:**
  Mild PACS JPEG compression ($Q=85$) yielded **0% False Alarm Rate** ($\text{FPR} = 0.0\%$), completely preserving clinical diagnosis integrity. Meanwhile, global perturbations (like exposure shifts) affect all blocks uniformly, whereas malicious tampering produces highly localized spatial anomaly spikes. This critical observation motivates our hybrid architecture: combining local SVD forensics with exact cryptographic block hashing (HMAC/Merkle) to eliminate false positives.
- **Key Output Files:**
  - `src/robustness.py`
  - `run_day6_robustness_benchmark.py`
  - `results/metrics/day6_robustness_results.csv`
  - `figures/day6_robustness_analysis.png`

---

### Day 7: Modern Generative AI (GAN & Diffusion) Manipulation Forensics
- **What was done in simple terms:**
  Today's most concerning medical fraud threat isn't simple copy-pasting—it is **generative AI deepfakes** (e.g., using CT-GAN or Latent Diffusion models like MedDDPM to inject artificial malignant tumors or erase real lung lesions). Following the M3Dsynth dataset framework:
  1. We simulated **GAN-based lesion synthesis** with characteristic high-frequency deconvolution checkerboard residuals and non-linear boundary gradients.
  2. We simulated **Diffusion model inpainting**, performing multi-step stochastic denoising that matches surrounding parenchymal texture statistics.
- **Key Finding:**
  Does classical SVD detect modern AI deepfakes? **Yes!**
  - GAN lesion insertion yielded **$F_1 = 1.00$** and **$\text{AUC} = 1.00$** due to generator spectral upsampling disruption.
  - Diffusion inpainting achieved **$F_1 = 0.80$**, **$\text{IoU} = 0.51$**, and **$\text{AUC} = 1.00$** with significant entropy changes ($\Delta H = 0.43$).
  This answers the paper's central question: classical linear algebraic SVD spectral decomposition retains strong sensitivity even against deep generative neural architectures!
- **Key Output Files:**
  - `src/ai_tampering.py`
  - `run_day7_ai_manipulation_benchmark.py`
  - `data/m3dsynth/` (paired authentic, manipulated, and mask images)
  - `results/metrics/day7_ai_manipulation_results.csv`
  - `figures/day7_ai_manipulation_detection.png`

---

### Day 8: SVD Feature Ablation Study & ROC-AUC Analysis
- **What was done in simple terms:**
  We extracted 5 different mathematical features from each CT block. But *which specific feature is doing the heavy lifting?* To answer this scientifically, we ran an ablation study where we tested each feature individually and in combination across 320 block evaluations covering all 5 tampering families (Region insertion, Copy-move, Splicing, Inpainting, and CT-GAN). We swept classification thresholds to plot Receiver Operating Characteristic (ROC) curves and computed the Area Under the Curve (AUC).
- **Key Finding:**
  - $\sigma_1$ (Dominant Singular Value) alone achieves **$\text{AUC} = 1.0000$** ($F_1 = 1.0000$).
  - Frobenius energy ($\sum\sigma_i^2$) also achieved **$\text{AUC} = 1.0000$**.
  - Spectral entropy ($H$) achieved **$\text{AUC} = 0.9892$**, showing high sensitivity to texture irregularity.
  - The combination of **$\sigma_1 + \text{Spectral Entropy}$** formed an optimal, lightweight ensemble ($\text{AUC} = 1.0000$, $F_1 = 1.0000$). This proves that we only need a compact 2-feature vector per block for cryptographic hashing, keeping cryptographic overhead minimal!
- **Key Output Files:**
  - `run_day8_feature_ablation.py`
  - `results/metrics/day8_feature_ablation_results.csv`
  - `figures/day8_roc_curves_ablation.png`




