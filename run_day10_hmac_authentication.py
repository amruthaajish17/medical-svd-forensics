import sys
sys.path.insert(0, 'src')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydicom.data import get_testdata_file

from preprocessing import load_dicom, normalize_image
from tampering import apply_region_tampering, apply_copy_move_tampering
from block_division import blocks_to_image
from crypto import (
    generate_secret_key,
    generate_image_manifest,
    verify_image_against_manifest
)

def run_hmac_authentication_suite():
    print("===========================================================================")
    print("DAY 10 EXPERIMENT: BLOCK-LEVEL SPATIAL HMAC-SHA256 AUTHENTICATION")
    print("===========================================================================")

    # 1. Load real CT scan
    dcm_path = get_testdata_file("CT_small.dcm")
    img_orig = normalize_image(load_dicom(dcm_path))
    block_size = 16
    h, w = img_orig.shape

    # 2. Key Generation & Reference Manifest
    secret_key = generate_secret_key()
    wrong_key = generate_secret_key()

    print("[+] Generated 256-bit cryptographically secure symmetric secret key.")
    manifest = generate_image_manifest(img_orig, secret_key, block_size=block_size, precision=4)
    print(f"[+] Signed {len(manifest)} blocks. Manifest size: {len(manifest) * 32} bytes HMAC payload.")

    # 3. Test Cases
    # Case A: Authentic CT verified with Correct Key
    valid_a, tamp_a, time_a = verify_image_against_manifest(img_orig, manifest, secret_key, block_size)

    # Case B: Region Tampered CT (16x16 local nodule insertion)
    img_tamp, mask_tamp = apply_region_tampering(img_orig, region_size=(16, 16), intensity_delta=0.35)
    valid_b, tamp_b, time_b = verify_image_against_manifest(img_tamp, manifest, secret_key, block_size)

    # Case C: Copy-Move attack (verifying coordinate binding prevents spatial block permutation)
    img_cm, mask_cm = apply_copy_move_tampering(img_orig, patch_size=(24, 24))
    valid_c, tamp_c, time_c = verify_image_against_manifest(img_cm, manifest, secret_key, block_size)

    # Case D: Authentic CT verified with WRONG Key (Adversarial impersonation attempt)
    valid_d, tamp_d, time_d = verify_image_against_manifest(img_orig, manifest, wrong_key, block_size)

    scenarios = [
        {"Scenario": "Authentic CT (Legitimate Key)", "Result": "VALID" if valid_a else "TAMPERED", "Tampered_Blocks": len(tamp_a), "Verification_Time_ms": time_a*1000.0, "Expected": "VALID"},
        {"Scenario": "Region Tampering (16x16)", "Result": "VALID" if valid_b else "TAMPERED", "Tampered_Blocks": len(tamp_b), "Verification_Time_ms": time_b*1000.0, "Expected": "TAMPERED"},
        {"Scenario": "Copy-Move Forgery", "Result": "VALID" if valid_c else "TAMPERED", "Tampered_Blocks": len(tamp_c), "Verification_Time_ms": time_c*1000.0, "Expected": "TAMPERED"},
        {"Scenario": "Authentic CT (Wrong Key)", "Result": "VALID" if valid_d else "TAMPERED", "Tampered_Blocks": len(tamp_d), "Verification_Time_ms": time_d*1000.0, "Expected": "TAMPERED"}
    ]

    results_df = pd.DataFrame(scenarios)
    csv_path = "results/metrics/day10_hmac_metrics.csv"
    results_df.to_csv(csv_path, index=False)
    print(f"\n[+] Saved HMAC evaluation metrics to '{csv_path}'.")

    for s in scenarios:
        status_sym = "[PASS]" if s["Result"] == s["Expected"] else "[FAIL]"
        print(f"  {status_sym} {s['Scenario']:<32} -> {s['Result']:<8} (Flagged {s['Tampered_Blocks']} blocks in {s['Verification_Time_ms']:.2f} ms)")

    # 4. Generate Visual Cryptographic Localization Map
    positions = [(m["x"], m["y"]) for m in manifest]
    hmac_binary_map = np.zeros(len(manifest))
    for t_idx in tamp_b:
        hmac_binary_map[t_idx] = 1.0

    hmac_loc_img = blocks_to_image(hmac_binary_map, positions, img_orig.shape, block_size)

    fig, axes = plt.subplots(1, 4, figsize=(18, 4.5))
    axes[0].imshow(img_orig, cmap="gray")
    axes[0].set_title("(a) Authentic CT (Signed)", fontweight='bold')
    axes[0].axis("off")

    axes[1].imshow(img_tamp, cmap="gray")
    axes[1].set_title("(b) Region Tampered CT", fontweight='bold')
    axes[1].axis("off")

    axes[2].imshow(mask_tamp, cmap="binary")
    axes[2].set_title("(c) Ground Truth Mask", fontweight='bold')
    axes[2].axis("off")

    axes[3].imshow(hmac_loc_img, cmap="Reds")
    axes[3].set_title(f"(d) HMAC Tag Rejections ({len(tamp_b)} Blocks)", fontweight='bold')
    axes[3].axis("off")

    plt.tight_layout()
    fig_path = "figures/day10_hmac_spatial_authentication.png"
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    print(f"\n[+] Saved HMAC spatial localization figure to '{fig_path}'.")
    print("===========================================================================\n")

if __name__ == "__main__":
    run_hmac_authentication_suite()
