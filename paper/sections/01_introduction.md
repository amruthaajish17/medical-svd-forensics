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
