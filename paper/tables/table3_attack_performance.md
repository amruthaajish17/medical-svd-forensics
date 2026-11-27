# Table 3: Forensic Detection Performance Across All Tampering Modalities

| attack_type | modified_area_px | accuracy | precision | recall | f1 | fpr | auc | iou | max_delta_entropy | max_delta_sigma1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Micro-Pixel (10 px) | 10 | 0.8750 | 0.0000 | 0.0000 | 0.0000 | 0.1250 | 0.5000 | 0.0049 | 0.2754 | 0.0518 |
| Region Insertion | 400 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.3906 | 0.1737 | 2.3350 |
| Copy-Move Cloning | 576 | 0.9844 | 1.0000 | 0.7500 | 0.8571 | 0.0000 | 1.0000 | 0.4802 | 0.6289 | 2.0033 |
| Splicing (Implant) | 400 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.3906 | 0.1036 | 1.1442 |
| Inpainting (Removal) | 400 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.3906 | 0.3436 | 0.5928 |