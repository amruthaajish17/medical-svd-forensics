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
