"""
run_all_experiments.py
--------------------------------------------------------------------------------
Master Execution Suite for Medical SVD Forensics & Cryptographic Authentication
Runs all daily experiments from Day 1 through Day 13 and prints a summary report.
--------------------------------------------------------------------------------
"""

import subprocess
import sys
import time

scripts = [
    ("Day 1: Baseline SVD Pipeline", "run_day1.py"),
    ("Day 1: Real CT Ingestion", "run_day1_real.py"),
    ("Day 2: Sensitivity Sweep", "run_day2_sensitivity_experiment.py"),
    ("Day 3: Anomaly Localization", "run_day3_anomaly_localization.py"),
    ("Day 4: Block Size Optimization", "run_day4_block_size_optimization.py"),
    ("Day 5: Multi-Attack Benchmark", "run_day5_multi_attack_benchmark.py"),
    ("Day 6: Robustness to Degradations", "run_day6_robustness_benchmark.py"),
    ("Day 7: AI/M3Dsynth Deepfake", "run_day7_ai_manipulation_benchmark.py"),
    ("Day 8: Feature Ablation & ROC", "run_day8_feature_ablation.py"),
    ("Day 9: Quantization & Stability", "run_day9_quantization_stability.py"),
    ("Day 10: Spatial HMAC Authentication", "run_day10_hmac_authentication.py"),
    ("Day 11: Merkle Tree Architecture", "run_day11_merkle_tree_authentication.py"),
    ("Day 12: Threat Model Security", "run_day12_security_threat_model.py"),
    ("Day 13: Publication Asset Suite", "run_day13_publication_assets.py")
]

def main():
    print("=" * 80)
    print("   MASTER EXECUTION SUITE: MEDICAL SVD FORENSICS & CRYPTOGRAPHIC AUTH")
    print("=" * 80)

    total_start = time.perf_counter()
    passed = 0

    for title, script in scripts:
        print(f"\n[RUNNING] {title} ({script})...")
        t0 = time.perf_counter()
        res = subprocess.run([sys.executable, script], capture_output=True, text=True)
        t_el = time.perf_counter() - t0

        if res.returncode == 0:
            print(f"  --> [PASS] Completed in {t_el:.2f}s")
            passed += 1
        else:
            print(f"  --> [FAIL] Error in {script} (code {res.returncode}):")
            print(res.stderr[:500])

    total_elapsed = time.perf_counter() - total_start
    print("\n" + "=" * 80)
    print(f"ALL EXPERIMENTS EXECUTED: {passed}/{len(scripts)} PASSED in {total_elapsed:.2f}s")
    print("=" * 80)

if __name__ == "__main__":
    main()
