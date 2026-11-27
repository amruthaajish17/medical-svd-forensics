# Table 5: Computational Runtime, Algorithmic Complexity, and Memory Footprint

| Pipeline_Stage | Time_per_Slice | Complexity | Memory_Overhead |
| --- | --- | --- | --- |
| CT DICOM Load & Normalize | 4.12 ms | O(N) | 128 KB |
| 16x16 Block SVD Decomposition | 8.54 ms | O(K * B^3) | 64 KB |
| Feature Extraction & Quantization | 1.20 ms | O(K) | 16 KB |
| Spatial HMAC-SHA256 Signatures | 1.85 ms | O(K) | 2 KB |
| Merkle Tree Construction & Root | 0.45 ms | O(K) | 32 Bytes |
| End-to-End Verification Pipeline | 16.16 ms | O(N) | < 250 KB |