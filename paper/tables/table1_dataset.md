# Table 1: Medical CT Dataset Overview & Manipulation Callset

| Dataset Category | Source / Modality | Sample Slices | Resolution | Target Attack Modality |
|---|---|---|---|---|
| **Authentic Host CT** | Real Clinical Thoracic DICOM | 64 blocks / slice | 128×128 (512×512 scaled) | Baseline Reference |
| **Micro-Scale Tampering** | Synthetic Pixel Perturbation | 50 slices | 128×128 | 1, 5, 10, 25, 100 Pixel Shifts |
| **Classical Forgery** | Controlled Spatial Transformations | 40 slices | 128×128 | Copy-Move, Splicing, Inpainting |
| **M3Dsynth Deepfake** | Generative AI Lesion Synthesis | 20 pairs | 128×128 | CT-GAN & Latent Diffusion (MedDDPM) |
| **Benign Clinical Drift** | Standard Scanner Noise & PACS | 30 slices | 128×128 | Gaussian Noise, JPEG (Q=85, 70), Blur |
