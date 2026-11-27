"""
src/crypto.py
--------------------------------------------------------------------------------
Spatial Block-Level HMAC-SHA256 Cryptographic Authentication Engine (Person B)

Implements:
  h_k = HMAC_K(F_tilde_k || x_k || y_k)
Provides:
- Unforgeable secret-key message authentication
- Spatial coordinate binding to defeat copy-move / block permutation attacks
- Constant-time verification to prevent timing attacks
--------------------------------------------------------------------------------
"""

import hmac
import hashlib
import secrets
import json
import time

from quantization import quantize_features, serialize_canonical_block
from svd_features import process_image_to_features

def generate_secret_key():
    """Generates a secure 256-bit (32-byte) pseudorandom key."""
    return secrets.token_bytes(32)

def compute_block_hmac(secret_key, quantized_dict, block_x, block_y):
    """
    Computes HMAC-SHA256 over canonical byte representation:
    h_k = HMAC_K(F_tilde_k || x_k || y_k)
    """
    canonical_data = serialize_canonical_block(quantized_dict, block_x, block_y)
    mac = hmac.new(secret_key, canonical_data, hashlib.sha256)
    return mac.hexdigest()

def verify_block_hmac(secret_key, quantized_dict, block_x, block_y, expected_hmac_hex):
    """
    Verifies block HMAC tag using constant-time comparison.
    """
    computed = compute_block_hmac(secret_key, quantized_dict, block_x, block_y)
    return hmac.compare_digest(computed, expected_hmac_hex)

def generate_image_manifest(image, secret_key, block_size=16, precision=4):
    """
    Extracts SVD features, quantizes, and produces full HMAC authentication manifest.
    
    Returns:
        list of dicts containing:
        { 'block_idx': i, 'x': x, 'y': y, 'hmac': h_k, 'features': quantized_dict }
    """
    feats, positions = process_image_to_features(image, block_size)
    manifest = []
    for idx, (f, (x, y)) in enumerate(zip(feats, positions)):
        q = quantize_features(f, precision_decimals=precision)
        h = compute_block_hmac(secret_key, q, x, y)
        manifest.append({
            "block_idx": idx,
            "x": int(x),
            "y": int(y),
            "hmac": h,
            "features": q
        })
    return manifest

def verify_image_against_manifest(test_image, manifest, secret_key, block_size=16, precision=4):
    """
    Authenticates test image blocks against reference manifest.
    
    Returns:
        is_authentic (bool), tampered_block_indices (list), verification_time (float)
    """
    start_t = time.perf_counter()
    feats, positions = process_image_to_features(test_image, block_size)
    
    tampered_indices = []
    
    for idx, (f, (x, y)) in enumerate(zip(feats, positions)):
        q = quantize_features(f, precision_decimals=precision)
        ref_entry = manifest[idx]
        
        # Verify both spatial alignment and cryptographic tag
        is_valid = verify_block_hmac(secret_key, q, ref_entry["x"], ref_entry["y"], ref_entry["hmac"])
        if not is_valid:
            tampered_indices.append(idx)
            
    elapsed = time.perf_counter() - start_t
    is_authentic = (len(tampered_indices) == 0)
    return is_authentic, tampered_indices, elapsed

if __name__ == "__main__":
    key = generate_secret_key()
    sample = {"sigma_1": 2.5, "entropy": 1.2}
    q = quantize_features(sample, 4)
    h_tag = compute_block_hmac(key, q, 16, 16)
    print("Crypto Module Ready.")
    print("HMAC Tag:", h_tag)
    print("Verify valid:", verify_block_hmac(key, q, 16, 16, h_tag))
