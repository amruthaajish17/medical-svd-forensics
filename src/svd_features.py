import numpy as np

def extract_svd_features(block):
    """Computes spectral characteristics from the singular values of a block."""
    U, S, Vt = np.linalg.svd(block, full_matrices=False)
    
    sigma_1 = S[0]
    sum_sigma = np.sum(S)
    sum_sigma_sq = np.sum(S**2)
    
    subdominant_energy = np.sum(S[1:]**2) if len(S) > 1 else 1e-6
    ratio = (S[0]**2) / (subdominant_energy + 1e-6)
    
    p = S / (sum_sigma + 1e-12)
    entropy = -np.sum(p * np.log2(p + 1e-12))
    
    return {
        "sigma_1": sigma_1,
        "sum_sigma": sum_sigma,
        "sum_sigma_sq": sum_sigma_sq,
        "ratio": ratio,
        "entropy": entropy
    }

def process_image_to_features(image, block_size=16):
    from block_division import divide_into_blocks
    blocks, positions = divide_into_blocks(image, block_size)
    features = [extract_svd_features(b) for b in blocks]
    return features, positions

if __name__ == "__main__":
    test_block = np.random.rand(16, 16)
    feats = extract_svd_features(test_block)
    print("5 feature values extracted:")
    for k, v in feats.items():
        print(f" - {k}: {v:.4f}")