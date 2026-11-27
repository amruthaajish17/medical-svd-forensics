## 2. Related Work

A comparative review of the literature demonstrates three distinct phases of medical image integrity research:

### 2.1 Classical SVD Watermarking
Early seminal work by Kang & Wei (2012) and Moghaddasi et al. (2014) established Singular Value Decomposition as an algebraic tool for image watermarking. Singular values exhibit algebraic stability against general affine transformations. However, conventional watermarking alters host pixel values, which can obscure minute microcalcifications or ground-glass lung nodules.

### 2.2 Passive Medical Image Forensics
Passive forensic algorithms detect manipulation without pre-embedded watermarks. El-Abbadi (2015) and Khudhair et al. explored copy-move forgery detection using block-matching and scale-invariant feature transforms (SIFT). While effective on natural scenes, medical CT images present smooth density gradients and repeated anatomical symmetries that frequently trigger false positives in feature-matching methods.

### 2.3 Generative Deepfakes & Modern Threat Models
The publication of CT-GAN by Mirsky et al. (2019) demonstrated that 3D conditional GANs could seamlessly inject or remove lung cancer nodules from CT scans without detection by experienced radiologists. Recently, Sikder et al. (2024) introduced M3Dsynth to study AI-synthesized manipulations. While deep detectors have been proposed, they act as opaque black boxes. Our work bridges this gap by leveraging intrinsic algebraic decomposition paired with lightweight cryptographic guarantees.

---
