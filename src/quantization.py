"""
src/quantization.py
--------------------------------------------------------------------------------
Deterministic Feature Quantization & Canonical Serialization (Person B)

Solves the floating-point non-determinism problem in cryptographic forensics:
- Quantizes continuous SVD singular features into fixed-point integer representations
- Enforces canonical lexicographical ordering of keys
- Provides reproducible, cross-platform UTF-8 byte serialization for SHA-256 / HMAC
--------------------------------------------------------------------------------
"""

import numpy as np
import json

def quantize_features(features_dict, precision_decimals=4):
    """
    Quantizes a floating-point feature dictionary into fixed-precision integer representations.
    
    Args:
        features_dict: dict of feature_name -> float value
        precision_decimals: integer number of decimal places to preserve (default 4)
        
    Returns:
        dict of feature_name -> integer (scaled by 10^precision_decimals)
    """
    scale = 10 ** precision_decimals
    quantized = {}
    for key in sorted(features_dict.keys()):
        val = features_dict[key]
        # Round to nearest integer after scaling
        quantized[key] = int(np.round(float(val) * scale))
    return quantized

def serialize_canonical_block(quantized_dict, block_x, block_y):
    """
    Generates a deterministic, canonical byte representation of a block's
    quantized SVD features bound to its spatial 2D coordinates (x, y).
    
    Format:
        x:<block_x>|y:<block_y>|<k1>:<v1>|<k2>:<v2>|...
    """
    parts = [f"x:{block_x}", f"y:{block_y}"]
    for k in sorted(quantized_dict.keys()):
        parts.append(f"{k}:{quantized_dict[k]}")
    canonical_str = "|".join(parts)
    return canonical_str.encode('utf-8')

if __name__ == "__main__":
    sample = {"sigma_1": 4.123456, "entropy": 1.987654}
    q = quantize_features(sample, precision_decimals=4)
    b = serialize_canonical_block(q, 16, 32)
    print("Quantized:", q)
    print("Canonical serialized bytes:", b)
