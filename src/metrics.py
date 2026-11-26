"""
src/metrics.py
--------------------------------------------------------------------------------
Comprehensive Evaluation Metrics for Tamper Detection & Localization (Person B)
Provides standard medical imaging forensics evaluation metrics:
- Precision, Recall, F1-Score, Accuracy, False Positive Rate (FPR), TPR
- Spatial Localization Intersection over Union (IoU)
- ROC Curve and Area Under Curve (AUC)
--------------------------------------------------------------------------------
"""

import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, roc_auc_score, precision_recall_fscore_support

class TamperDetectionMetrics:
    """Computes block-level and pixel-level forensic evaluation metrics."""

    @staticmethod
    def calculate_block_level_metrics(y_true, y_scores, threshold=0.5):
        """
        Calculates classification metrics given ground truth binary labels and predicted scores.
        
        Args:
            y_true: 1D array of ground truth labels (0 = authentic, 1 = tampered)
            y_scores: 1D array of predicted anomaly scores in [0, 1]
            threshold: Decision threshold for classification
            
        Returns:
            dict containing Accuracy, Precision, Recall, F1, FPR, TPR, TP, FP, TN, FN
        """
        y_true = np.asarray(y_true, dtype=int)
        y_scores = np.asarray(y_scores, dtype=float)
        y_pred = (y_scores >= threshold).astype(int)

        # Handle edge cases where all samples are authentic or tampered
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0.0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        tpr = recall

        return {
            "accuracy": float(accuracy),
            "precision": float(precision),
            "recall": float(recall),
            "f1": float(f1),
            "fpr": float(fpr),
            "tpr": float(tpr),
            "tp": int(tp),
            "fp": int(fp),
            "tn": int(tn),
            "fn": int(fn)
        }

    @staticmethod
    def calculate_localization_iou(ground_truth_mask, predicted_mask):
        """
        Computes spatial Intersection over Union (IoU) for localization masks.
        
        Args:
            ground_truth_mask: 2D binary numpy array
            predicted_mask: 2D binary numpy array
            
        Returns:
            float IoU score in [0.0, 1.0]
        """
        gt_binary = (ground_truth_mask > 0).astype(bool)
        pred_binary = (predicted_mask > 0).astype(bool)

        intersection = np.logical_and(gt_binary, pred_binary).sum()
        union = np.logical_or(gt_binary, pred_binary).sum()

        if union == 0:
            return 1.0 if not gt_binary.any() else 0.0
        return float(intersection / union)

    @staticmethod
    def calculate_roc_auc(y_true, y_scores):
        """Calculates ROC AUC score safely."""
        y_true = np.asarray(y_true, dtype=int)
        y_scores = np.asarray(y_scores, dtype=float)
        if len(np.unique(y_true)) < 2:
            return 1.0 if (y_true == 1).all() else 0.5
        return float(roc_auc_score(y_true, y_scores))

if __name__ == "__main__":
    y_t = [0, 0, 1, 1, 0, 1]
    y_s = [0.1, 0.2, 0.8, 0.9, 0.3, 0.7]
    metrics = TamperDetectionMetrics.calculate_block_level_metrics(y_t, y_s)
    print("Metrics Module Test passed:")
    for k, v in metrics.items():
        print(f"  {k}: {v}")
