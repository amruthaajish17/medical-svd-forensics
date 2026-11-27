## 5. Security Architecture & Threat Analysis

We formalized security under Kerckhoffs's principle against an active adversary. Five attack vectors were systematically evaluated (**Figure 12**):

1. **Pixel-Only Attacker**: An adversary modifies pixel data but cannot forge HMAC tags. **Result:** $100\%$ intercepted via Merkle root mismatch.
2. **Coordinate Metadata Attacker**: An adversary shifts $(x, y)$ coordinates in the header. **Result:** Defeated; spatial coordinate binding causes signature rejection.
3. **Key-Guessing Attacker**: An unauthorized party attempts verification with an invalid key. **Result:** Constant-time verification rejects $100\%$ of blocks.
4. **Manifest Tampering Attacker**: An adversary modifies the stored SVD features. **Result:** Defeated; the HMAC tag does not correspond to forged feature values.
5. **Replay / Block-Swap Attacker**: An adversary copies an authentic tag from Block $A$ to Block $B$. **Result:** Coordinate mismatch $(x_A, y_A) \neq (x_B, y_B)$ causes immediate cryptographic failure.

---
