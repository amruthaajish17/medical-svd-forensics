## 6. Discussion & Limitations

- **Benign Degradations:** Lossy PACS JPEG compression ($Q=85$) yielded **$0.0\%$ False Alarm Rate**, demonstrating that mild compression artifacts remain well below malicious tampering thresholds. However, global exposure shifts cause uniform block changes, underscoring the necessity of our cryptographic Merkle layer for authoritative validation.
- **Clinical Scope:** Our evaluations were performed on benchmark thoracic CT scans. Real clinical deployment requires validating diverse anatomical protocols (brain CT, contrast-enhanced abdominal CT) and integration with standard DICOM PACS gateways.

---
