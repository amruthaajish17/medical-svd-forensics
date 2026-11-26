"""
src/robustness.py
--------------------------------------------------------------------------------
Benign Transformations and Clinical Degradation Simulator (Person B)

Tests whether the SVD forensic detector falsely triggers on harmless clinical
image degradations:
- Gaussian sensor / thermal noise
- Lossy JPEG / PACS transmission compression
- Optical / scanner point-spread function blur
- Global intensity / exposure drift
--------------------------------------------------------------------------------
"""

import numpy as np
import cv2

def apply_gaussian_noise(image, var=0.001, seed=42):
    """Adds zero-mean Gaussian sensor noise with specified variance."""
    np.random.seed(seed)
    sigma = np.sqrt(var)
    noise = np.random.normal(0, sigma, image.shape)
    return np.clip(image + noise, 0.0, 1.0)

def apply_jpeg_compression(image, quality=80):
    """Simulates lossy compression from network PACS image archival."""
    img_uint8 = (np.clip(image, 0.0, 1.0) * 255).astype(np.uint8)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    result, encimg = cv2.imencode('.jpg', img_uint8, encode_param)
    decimg = cv2.imdecode(encimg, cv2.IMREAD_GRAYSCALE)
    return decimg.astype(np.float64) / 255.0

def apply_gaussian_blur(image, kernel_size=(3, 3), sigma=0.8):
    """Simulates slight point spread function blur from patient micro-motion."""
    return cv2.GaussianBlur(image, kernel_size, sigmaX=sigma, sigmaY=sigma)

def apply_intensity_drift(image, delta=0.02):
    """Simulates scanner calibration drift or slight exposure variation."""
    return np.clip(image + delta, 0.0, 1.0)

if __name__ == "__main__":
    t_img = np.random.rand(64, 64)
    print("Robustness module ready.")
    print("Noise:", apply_gaussian_noise(t_img).shape)
    print("JPEG:", apply_jpeg_compression(t_img).shape)
    print("Blur:", apply_gaussian_blur(t_img).shape)
    print("Drift:", apply_intensity_drift(t_img).shape)
