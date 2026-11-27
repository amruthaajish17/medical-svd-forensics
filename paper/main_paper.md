# Passive SVD Spectral Forensics and Lightweight Cryptographic Spatial Authentication for Medical Computed Tomography (CT) Images

**Authors:** Amrutha Ajish, Athira Anil  
**Institution:** Department of Artificial Intelligence and Data Science  
**Keywords:** Medical Image Forensics, Singular Value Decomposition (SVD), CT Tampering Detection, Spectral Entropy, HMAC-SHA256, Merkle Tree, M3Dsynth, AI Inpainting.

---

## Abstract
Modern medical Picture Archiving and Communication Systems (PACS) face an emerging security crisis: the malicious manipulation of diagnostic scans via generative deep learning (e.g., CT-GAN, diffusion inpainting) and localized clinical forgery (copy-move and tissue splicing). Although deep neural networks can detect synthetic textures, they lack mathematical explainability, require high computational overhead, and remain vulnerable to adversarial evasion. 

In this paper, we propose a lightweight, hybrid forensic framework combining **local Singular Value Decomposition (SVD) spectral analysis** with **spatial cryptographic authentication**. First, the CT slice is partitioned into non-overlapping $16 \times 16$ blocks, from which intrinsic spectral properties—most notably dominant singular value ($\sigma_1$) and spectral entropy ($H$)—are extracted. Second, continuous singular values are mapped into a deterministic fixed-point canonical representation to eliminate floating-point non-determinism. Third, each block is bound to its spatial 2D coordinates via secret-keyed $\text{HMAC-SHA256}$ tags, aggregated into a balanced hierarchical **Merkle Tree**.

Extensive experimental evaluations across clinical DICOM CT scans, controlled micro-pixel manipulations ($1$ to $100$ pixels), classical spatial forgeries, and modern AI generative inpainting (M3Dsynth framework) demonstrate that:
1. Local SVD spectral characteristics achieve **$F_1 = 1.00$** and **$\text{AUC} = 1.00$** on region insertion, splicing, and generative deepfake lesion injections.
2. The dual-feature ensemble ($\sigma_1 + H$) provides state-of-the-art discriminative power while maintaining resilience against mild PACS JPEG compression ($Q=85$) with a **$0.0\%$ False Positive Rate**.
3. Cryptographic Merkle tree verification guarantees $O(1)$ global integrity verification and isolates localized tampering to exact 2D pixel coordinates in **$16.16\text{ ms}$** per slice.
Our framework provides a clinically viable, mathematically defensible, and zero-pixel-distortion authentication system suitable for real-time PACS deployment.

---

## 1. Introduction
Computed Tomography (CT) imaging serves as a foundational pillar in modern radiological diagnosis, oncology treatment planning, and surgical intervention. However, the digitization of clinical workflows and network-connected Picture Archiving and Communication Systems (PACS) expose medical scans to severe integrity threats. In particular, malicious adversaries or fraudulent actors may alter patient scans to forge insurance claims, misdiagnose illnesses, or inject false malignancies using automated generative deep learning pipelines such as CT-GAN.

Prior defensive approaches broadly divide into two paradigms:
1. **Active Watermarking**: Embeds pseudo-random bit sequences directly into image transform domains (DCT, DWT). While effective for provenance, watermarking inherently introduces irreversible noise into diagnostic pixel arrays, raising clinical and regulatory concerns under FDA/CE standards.
2. **Deep Learning Detectors**: Convolutional and transformer-based passive forensics attempt to classify manipulated regions. However, they suffer from domain generalization collapse when evaluated on unseen scanner calibrations, require heavy GPU resources, and cannot provide mathematical proof of integrity.

### Research Questions
In this paper, we address two fundamental research questions:
- **Primary RQ:** *Do local SVD spectral characteristics provide a reliable intrinsic signature for detecting and localizing tampering in medical CT images?*
- **Secondary RQ:** *Can these local signatures be cryptographically bound to provide deterministic image authentication without modifying the diagnostic pixel array?*

### Key Contributions
- **Passive SVD Forensic Core**: We establish that localized CT manipulations disrupt the low-rank singular value spectrum and spectral entropy of anatomical tissue blocks, yielding a sensitive passive forensic signal.
- **Deterministic Feature Quantization**: We solve the floating-point cross-platform non-determinism problem, enabling continuous singular value descriptors to interface with exact cryptographic hash primitives.
- **Hierarchical Spatial Merkle Tree**: We propose a coordinate-bound HMAC and Merkle tree structure that provides $O(1)$ whole-image validation and $O(\log N)$ spatial tamper localization.
- **Empirical Validation**: We validate the system against micro-pixel attacks, classical forgeries (copy-move, splicing, inpainting), and modern generative deepfakes (M3Dsynth), achieving real-time execution ($16.16\text{ ms}$).

---

## 2. Related Work
A comparative review of the literature demonstrates three distinct phases of medical image integrity research:

### 2.1 Classical SVD Watermarking
Early seminal work by Kang & Wei (2012) and Moghaddasi et al. (2014) established Singular Value Decomposition as an algebraic tool for image watermarking. Singular values exhibit algebraic stability against general affine transformations. However, conventional watermarking alters host pixel values, which can obscure minute microcalcifications or ground-glass lung nodules.

### 2.2 Passive Medical Image Forensics
Passive forensic algorithms detect manipulation without pre-embedded watermarks. El-Abbadi (2015) and Khudhair et al. explored copy-move forgery detection using block-matching and scale-invariant feature transforms (SIFT). While effective on natural scenes, medical CT images present smooth density gradients and repeated anatomical symmetries that frequently trigger false positives in feature-matching methods.

### 2.3 Generative Deepfakes & Modern Threat Models
The publication of CT-GAN by Mirsky et al. (2019) demonstrated that 3D conditional GANs could seamlessly inject or remove lung cancer nodules from CT scans without detection by experienced radiologists. Recently, Sikder et al. (2024) introduced M3Dsynth to study AI-synthesized manipulations. While deep detectors have been proposed, they act as opaque black boxes. Our work bridges this gap by leveraging intrinsic algebraic decomposition paired with lightweight cryptographic guarantees.

---

## 3. Proposed Methodology

The overall architecture of our dual-layer forensic framework is illustrated in **Figure 1**.

```
               [ Input CT Image (DICOM) ]
                           │
                           ▼
          [ Block Division (16x16 Non-overlapping) ]
                           │
                           ▼
         [ Local Singular Value Decomposition (SVD) ]
                           │
            ┌──────────────┴──────────────┐
            ▼                             ▼
   [ Passive Forensics ]         [ Cryptographic Layer ]
     Anomaly Vector ΔF            Canonical Quantization F̃
     Spatial Heatmaps             HMAC-SHA256 (F̃ || x || y)
     Threshold Classifier         Hierarchical Merkle Tree
            │                             │
            ▼                             ▼
   Local Lesion Discovery        O(1) Global Root Integrity
```

### 3.1 Local SVD Feature Extraction
For each normalized block $B_k \in \mathbb{R}^{B \times B}$, Singular Value Decomposition decomposes the block matrix into:
$$B_k = U_k \Sigma_k V_k^T$$
where $U_k$ and $V_k$ are orthogonal matrices and $\Sigma_k = \text{diag}(\sigma_1, \sigma_2, \dots, \sigma_B)$ with $\sigma_1 \ge \sigma_2 \ge \dots \ge \sigma_B \ge 0$.

From $\Sigma_k$, we extract five distinct mathematical descriptors:
1. **Dominant Singular Value:** $\sigma_1$ (captures primary energy / baseline density).
2. **Total Nuclear Norm:** $\sum_{i=1}^B \sigma_i$ (trace / overall luminance).
3. **Frobenius Energy:** $\sum_{i=1}^B \sigma_i^2$ (total structural variance).
4. **Energy Ratio:** $\sigma_1^2 / (\sum_{i=2}^B \sigma_i^2 + \epsilon)$ (relative structural dominance).
5. **Spectral Entropy:**
   $$p_i = \frac{\sigma_i}{\sum \sigma_j}, \quad H = -\sum_{i=1}^B p_i \log_2(p_i)$$
   Spectral entropy quantifies textural disorder: smooth parenchymal tissue displays low entropy, whereas synthetic noise, splicing boundaries, and GAN checkerboard artifacts significantly elevate $H$.

### 3.2 Canonical Quantization & Coordinate Binding
Standard cryptographic hash algorithms (SHA-256) exhibit an avalanche effect: a single bit discrepancy alters the output completely. Because floating-point representations differ across architectures, we apply canonical fixed-point scaling:
$$\tilde{F}_k = \text{round}\left(F_k \times 10^d\right)$$
where $d=4$ decimal precision preserves feature variance while ensuring bitwise cross-platform stability.

To prevent block permutation and replay attacks, we serialize $\tilde{F}_k$ into an ordered byte string strictly bound to spatial coordinates $(x_k, y_k)$:
$$S_k = \text{UTF-8}\left(x_k \parallel y_k \parallel \text{sorted\_keys}(\tilde{F}_k)\right)$$

### 3.3 Spatial HMAC and Hierarchical Merkle Tree
Under symmetric key $K$, each block signature is computed as:
$$h_k = \text{HMAC-SHA256}_K(S_k)$$
These $N$ block signatures form the leaf nodes of a balanced binary Merkle Tree. Pairwise parent nodes are computed as:
$$\text{parent} = \text{SHA-256}(\text{left} \parallel \text{right})$$
until reaching the unique **32-byte Merkle Root Hash ($R$)**. The root $R$ can be appended to the DICOM standard metadata header (e.g. Tag `(0028, 7FE0)`) without touching any image pixels.

---

## 4. Experimental Setup & Results

### 4.1 Block Size Optimization
We evaluated block sizes $8 \times 8$, $16 \times 16$, and $32 \times 32$ to determine the optimal spatial-computational trade-off. As detailed in **Table 4**, $16 \times 16$ blocks achieved an optimal balance:
- $F_1 = 1.0000$, $\text{AUC} = 1.0000$
- Runtime: $13.38\text{ ms}$ per slice (compared to $29.00\text{ ms}$ for $8 \times 8$)
- Spatial IoU: $0.4741$ (providing crisp boundary localization).

### 4.2 Multi-Attack Forensic Performance
We benchmarked the passive SVD detector across five distinct tampering categories:
1. **Micro-Pixel Manipulation:** 1 to 100 random pixel shifts.
2. **Region Insertion:** $16 \times 16$ synthetic tumor injection.
3. **Copy-Move Forgery:** $24 \times 24$ internal parenchymal nodule cloning.
4. **Tissue Splicing:** $20 \times 20$ foreign lesion blending.
5. **Inpainting:** $20 \times 20$ Navier-Stokes and mean-interpolated tumor removal.

As reported in **Table 3** and visualized in **Figure 2**:
- **Region Insertion:** $F_1 = 1.0000$, $\text{AUC} = 1.0000$
- **Tissue Splicing:** $F_1 = 1.0000$, $\text{AUC} = 1.0000$
- **Inpainting (Removal):** $F_1 = 1.0000$, $\text{AUC} = 1.0000$
- **Copy-Move:** $F_1 = 0.8571$, $\text{AUC} = 1.0000$.

### 4.3 Generative Deepfakes (M3Dsynth)
Under modern AI deepfake tampering (**Figure 4**):
- **CT-GAN Lesion Insertion:** $F_1 = 1.0000$, $\text{AUC} = 1.0000$ ($\text{Max } \Delta H = 0.0887$). High-frequency generator deconvolution artifacts disrupt the singular value spectrum.
- **Diffusion Semantic Inpainting (MedDDPM):** $F_1 = 0.8000$, $\text{AUC} = 1.0000$ ($\text{Max } \Delta H = 0.4303$). Stochastic denoising significantly shifts local spectral entropy.

### 4.4 Feature Ablation Study
ROC-AUC analysis across 320 block evaluations (**Table 2** and **Figure 3**) revealed:
- $\sigma_1$ alone achieves $\text{AUC} = 1.0000$.
- Spectral Entropy $H$ alone achieves $\text{AUC} = 0.9892$.
- The dual ensemble **$(\sigma_1 + H)$** delivers perfect discrimination ($\text{AUC} = 1.0000$, $F_1 = 1.0000$) while minimizing computational overhead.

---

## 5. Security Architecture & Threat Analysis
We formalized security under Kerckhoffs's principle against an active adversary. Five attack vectors were systematically evaluated (**Figure 12**):

1. **Pixel-Only Attacker**: An adversary modifies pixel data but cannot forge HMAC tags. **Result:** $100\%$ intercepted via Merkle root mismatch.
2. **Coordinate Metadata Attacker**: An adversary shifts $(x, y)$ coordinates in the header. **Result:** Defeated; spatial coordinate binding causes signature rejection.
3. **Key-Guessing Attacker**: An unauthorized party attempts verification with an invalid key. **Result:** Constant-time verification rejects $100\%$ of blocks.
4. **Manifest Tampering Attacker**: An adversary modifies the stored SVD features. **Result:** Defeated; the HMAC tag does not correspond to forged feature values.
5. **Replay / Block-Swap Attacker**: An adversary copies an authentic tag from Block $A$ to Block $B$. **Result:** Coordinate mismatch $(x_A, y_A) \neq (x_B, y_B)$ causes immediate cryptographic failure.

---

## 6. Discussion & Limitations
- **Benign Degradations:** Lossy PACS JPEG compression ($Q=85$) yielded **$0.0\%$ False Alarm Rate**, demonstrating that mild compression artifacts remain well below malicious tampering thresholds. However, global exposure shifts cause uniform block changes, underscoring the necessity of our cryptographic Merkle layer for authoritative validation.
- **Clinical Scope:** Our evaluations were performed on benchmark thoracic CT scans. Real clinical deployment requires validating diverse anatomical protocols (brain CT, contrast-enhanced abdominal CT) and integration with standard DICOM PACS gateways.

---

## 7. Conclusion
In this work, we developed and validated a dual-layer medical CT forensics architecture uniting passive local SVD spectral feature analysis with spatial Merkle tree cryptography. Experiments demonstrate that SVD spectral entropy and dominant singular values provide an intrinsic signature capable of detecting both classical forgeries and modern generative AI deepfakes ($F_1 \ge 0.80, \text{AUC} = 1.0000$). Coupled with our coordinate-bound Merkle authentication layer, the system achieves $O(1)$ whole-image verification and localized tamper tracing in $16.16\text{ ms}$ with zero diagnostic pixel modification.

---

## References
Please see `paper/references/references.bib` for the complete BibTeX citation repository.
