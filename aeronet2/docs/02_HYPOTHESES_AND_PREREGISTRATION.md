# 02 — Hypotheses, lineage and pre-registration template

## Lineage (keep this; judges respect an honest trail)
| ID | Statement | Status |
|---|---|---|
| H1 | In a **calibrated** linear-Gaussian model with i.i.d. links, no adaptive policy beats the best open-loop schedule by more than a practically negligible margin. | Supported (≤2% everywhere; noise-like triggers equal/worse). Equivalence at ±1% **not** yet established at 20–30 seeds — needs more seeds. |
| H2 (original) | Adaptive gain grows with sensing/link **heterogeneity**. | **Falsified** in simulation: heterogeneous nominal scenarios show ≤2% gain, attributable to open-loop allocation. |
| H2′ (post-hoc) | Adaptive gain arises when the model is **inconsistent** with reality (mismatch), via consistency-aware triggering. | Supported qualitatively on 12 exploratory + 8 held-out configurations (3–10%). *Proposed after seeing data → exploratory until the pre-registered run.* |
| H3 | Peer-state-aware VoI adds gain beyond consistency monitoring alone. | Mixed: strong at low budgets (≤20), no better (or slightly worse) at budgets ≥ 40. |
| H4 | Exact measurement sharing outperforms covariance-intersection estimate sharing at equal message count. | Supported (≈1.7%, nominal, budget 40). |
| H5 | The mismatch gain follows a power law in a mismatch index. | **Not supported** (held-out R² < 0). Replace by a mechanistic hypothesis (below). |
| H6 | Qualitative H1/H2′ pattern survives on hardware. | Untested. |
| H5′ (to derive) | Gain ≈ fraction of the budget that can be concentrated into mismatch episodes → non-monotone in duty cycle; peaks at intermediate duty. | Unproven. Must be derived, then tested on *new* configs. |

## Pre-registration template (fill in, commit, tag `prereg-v1` BEFORE the confirmatory run)
- **Primary outcome:** steady-state position RMSE (t ≥ burn-in), paired by seed against `periodic` at the same budget.
- **Primary contrasts (Holm-corrected):** voi_psa vs periodic and innov vs periodic in {nominal, mismatch}.
- **Equivalence margin (nominal):** ±1% of periodic RMSE; required n computed from pilot SD (pilot SD of paired difference ≈ 0.03–0.05 → n ≳ 100).
- **Scenarios & budgets:** list exactly (write the `Scenario(...)` calls).
- **Seeds:** 40000–40099 (reserved; never used for tuning).  **Run once.**
- **Exclusions:** none permitted post hoc; failed trials are reported, not dropped (`stats.py` raises on NaN).
- **Secondary:** bytes, delivered fraction, NEES (consistency), gap closed vs full-information bound.
- **Stopping rule:** fixed n. **Deviations:** logged in the journal with reason and date.
- **What would falsify H2′:** CI for voi_psa − periodic in the mismatch scenario includes 0 or is positive.
- **What would falsify H1:** nominal CI excludes ±1% in favour of an adaptive policy.
