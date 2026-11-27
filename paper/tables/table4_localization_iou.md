# Table 4: Spatial Localization Resolution (IoU) and Trade-Off by Block Size

| block_size | block_dim | num_blocks | runtime_ms | accuracy | precision | recall | f1 | fpr | auc | iou |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 8x8 | 8 | 256 | 31.3031 | 0.9805 | 0.8696 | 0.9091 | 0.8889 | 0.0128 | 0.9965 | 0.6596 |
| 16x16 | 16 | 64 | 12.2561 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.4741 |
| 32x32 | 32 | 16 | 7.5220 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 0.0000 | 1.0000 | 0.2913 |