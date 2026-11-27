"""
src/ai_tampering.py
--------------------------------------------------------------------------------
AI-Generated CT Manipulation & M3Dsynth Simulation Engine (Person A & Person B)

Simulates state-of-the-art generative deepfake and inpainting manipulations:
1. GAN-Generated Lesion Insertion:
   - High-fidelity synthetic nodule synthesis with multi-scale frequency residuals
   - Realistic non-linear edge gradient blending (mimicking CT-GAN/StyleGAN-Med)
2. Diffusion-Based Semantic Inpainting:
   - Multi-step denoising synthesis mimicking latent diffusion models (e.g. MedDDPM)
   - Replaces lung parenchyma with synthetic tissue matching regional Hounsfield statistics
--------------------------------------------------------------------------------
"""

import numpy as np
import cv2
from pathlib import Path

def generate_synthetic_lesion_nodule(size=24, intensity_scale=0.35, seed=42):
    """
    Generates a realistic 2D medical CT pulmonary nodule morphology with
    irregular spiculation, internal density variation, and boundary decay.
    """
    np.random.seed(seed)
    yy, xx = np.ogrid[-size//2:size//2, -size//2:size//2]
    radius = np.sqrt(xx**2 + yy**2)
    max_r = size / 2.5

    # Core spherical attenuation profile
    core = np.clip(1.0 - (radius / max_r)**2, 0.0, 1.0)

    # Add realistic irregular spiculation / contour lobulation
    angles = np.arctan2(yy, xx)
    lobulation = 0.15 * np.sin(5 * angles) + 0.10 * np.cos(3 * angles)
    nodule_mask = (radius <= (max_r * (1.0 + lobulation)))

    # Internal heterogeneous density texture (mimicking soft-tissue lesion attenuation)
    internal_texture = np.random.normal(0.85, 0.1, (size, size))
    nodule = core * internal_texture * nodule_mask * intensity_scale

    # Smooth boundary transitions
    nodule = cv2.GaussianBlur(nodule, (3, 3), sigmaX=0.8)
    return nodule

def apply_gan_lesion_insertion(image, nodule_size=24, position=None, intensity=0.40, seed=42):
    """
    Simulates GAN-based lesion injection into healthy CT parenchyma.
    Introduces subtle high-frequency spectral artifacts characteristic of generator upsampling.
    """
    h, w = image.shape
    tampered = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    if position is None:
        pos_y, pos_x = int(h * 0.45), int(w * 0.50)
    else:
        pos_y, pos_x = position

    nodule = generate_synthetic_lesion_nodule(size=nodule_size, intensity_scale=intensity, seed=seed)
    
    # Simulate GAN spectral upsampling artifact (checkerboard / deconvolution high-freq residual)
    yy, xx = np.indices((nodule_size, nodule_size))
    gan_artifact = 0.03 * ((xx % 2) - 0.5) * ((yy % 2) - 0.5)
    nodule_with_artifact = np.clip(nodule + gan_artifact * (nodule > 0.05), 0.0, 1.0)

    end_y = min(pos_y + nodule_size, h)
    end_x = min(pos_x + nodule_size, w)
    nh, nw = end_y - pos_y, end_x - pos_x

    tampered[pos_y:end_y, pos_x:end_x] = np.clip(
        tampered[pos_y:end_y, pos_x:end_x] + nodule_with_artifact[:nh, :nw], 0.0, 1.0
    )
    mask[pos_y:end_y, pos_x:end_x] = (nodule[:nh, :nw] > 0.05).astype(np.uint8)

    return tampered, mask

def apply_diffusion_inpainting(image, inpaint_size=28, position=None, seed=42):
    """
    Simulates diffusion model latent inpainting: reconstructs the region using
    synthetic multi-scale stochastic denoising matching host mean and variance.
    """
    np.random.seed(seed)
    h, w = image.shape
    tampered = image.copy()
    mask = np.zeros((h, w), dtype=np.uint8)

    if position is None:
        pos_y, pos_x = int(h * 0.35), int(w * 0.35)
    else:
        pos_y, pos_x = position

    end_y = min(pos_y + inpaint_size, h)
    end_x = min(pos_x + inpaint_size, w)
    nh, nw = end_y - pos_y, end_x - pos_x

    # Sample surrounding host tissue statistics
    surrounding = image[max(0, pos_y-10):min(h, end_y+10), max(0, pos_x-10):min(w, end_x+10)]
    mean_val = np.mean(surrounding)
    std_val = np.std(surrounding)

    # Multi-resolution synthetic diffusion denoising pattern
    diffusion_field = np.random.normal(mean_val, std_val * 0.6, (nh, nw))
    diffusion_field = cv2.GaussianBlur(diffusion_field, (5, 5), sigmaX=1.2)
    
    # Seamless alpha-edge blending
    yy, xx = np.ogrid[:nh, :nw]
    dist_from_edge = np.minimum(np.minimum(yy, nh - 1 - yy), np.minimum(xx, nw - 1 - xx))
    alpha = np.clip(dist_from_edge / 4.0, 0.0, 1.0)

    original_patch = tampered[pos_y:end_y, pos_x:end_x]
    tampered[pos_y:end_y, pos_x:end_x] = original_patch * (1.0 - alpha) + diffusion_field * alpha
    mask[pos_y:end_y, pos_x:end_x] = 1

    return tampered, mask

def setup_m3dsynth_dataset_hierarchy(base_dir="data/m3dsynth"):
    """Initializes local dataset directories for M3Dsynth benchmarks."""
    for sub in ["authentic", "manipulated", "masks"]:
        p = Path(base_dir) / sub
        p.mkdir(parents=True, exist_ok=True)
    return base_dir

if __name__ == "__main__":
    t_img = np.zeros((128, 128))
    g_img, g_mask = apply_gan_lesion_insertion(t_img)
    d_img, d_mask = apply_diffusion_inpainting(t_img)
    print("AI Tampering Module Initialized.")
    print(f"GAN nodule modified pixels: {g_mask.sum()}")
    print(f"Diffusion inpainting modified pixels: {d_mask.sum()}")
