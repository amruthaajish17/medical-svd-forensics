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
