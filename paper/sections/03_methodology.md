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
