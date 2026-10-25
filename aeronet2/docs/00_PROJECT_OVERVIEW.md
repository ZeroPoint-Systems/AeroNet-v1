# AeroNet2 — project overview (revamped)

## Working title
**When does communication policy matter? Calibrated-model optimality and mismatch-driven gains in budget-limited,
lossy, decentralised estimation.**

## Research questions (one lead, two supporting)
- **RQ (lead):** In decentralised tracking with a fixed message budget over lossy, delayed links, *when* does an
  adaptive (data-driven) communication policy beat the best time-triggered schedule, and by how much?
- RQ-a: Which component of an adaptive policy produces the gain — consistency monitoring, receiver/value awareness,
  or closed-loop feedback about peers?
- RQ-b: Does the simulated picture survive real sensors, clocks and a real network (sim-to-real gap)?

This replaces the earlier two competing questions (README "critical information boundary" vs plan-document
"communication-efficient policy"). The exploration showed there is **no sharp boundary** in this model class
(each agent is individually observable, so error is always bounded); the interesting structure is *regime-dependent*.

## What the evidence currently says (all from `results/RESULTS.md`; exploratory unless marked)
1. **Simulator validated.** Exact delayed-measurement fusion equals a brute-force batch solution; simulated local and
   centralised RMSE match analytic Riccati steady states; filter NEES ≈ 4 when the model is right (tests pass).
2. **v1 negative result explained.** Seed overlap (35 of 180 noise streams), un-aligned stale peer states, and triggers that
   were pure noise — not "communication is useless".
3. **Null regime (calibrated model).** No policy beats periodic by more than ~2%. Noise-like triggers (random, delta,
   innovation) are the same or slightly *worse* than periodic. The only nominal signal is an *open-loop* VoI schedule
   (−1.9% at budget 40, Holm p = 0.02; not significant at budgets 10, 20, 80) — suggestive of smarter allocation, not feedback; treat as unconfirmed.
4. **Mismatch regime (intermittent unmodelled manoeuvres).** PSA-VoI beats periodic by 3.4 / 5.2 / 9.0 / 7.6 % RMSE at
   budgets 10 / 20 / 40 / 80 messages per agent (30 fresh seeds, Holm-adjusted p ≤ 0.001 at every budget; 0.0008 is the bootstrap resolution floor); at budget 40 it closes about
   34% of the gap to the full-information bound versus 9% for periodic.
5. **Decomposition.** The consistency signal is the main driver (paced innovation-only gets −8.6% at budget 40);
   peer-state-aware VoI adds mostly at low budgets (budget 10: PSA −3.4% vs innovation-only −1.0% vs open-loop VoI −0.8%).
6. **Exact measurement sharing beats CI estimate sharing** by ≈1.6–1.8% at budget 40 despite CI sending more bytes.
7. **Law attempt — NOT confirmed.** Power laws in a mismatch index fit the exploratory sweep (R² 0.5–0.6) but fail on 8 new
   held-out configurations (out-of-sample R² −0.75 and −0.25). What *did* hold: the gain was positive (3–8%) in all
   20 configurations and is not monotone — it falls when manoeuvres become the norm (high duty cycle).

## Contribution candidates, honestly ranked
| Rung | Claim | Status |
|---|---|---|
| 1 | Validated open testbed + corrected methodology | Done (needs your ownership and review) |
| 2 | Regime map: null vs mismatch-driven adaptive gain, with decomposition | Supported in simulation; needs pre-registered confirmation and hardware |
| 3 | PSA-VoI as a new method | Unverified novelty; components are known ideas — literature check decides |
| 4 | Predictive law for the gain | **Not established.** Mechanistic hypothesis to derive: gain ≈ how well a fixed budget can be *concentrated* into mismatch episodes |

## Claims policy (write this on the first page of your journal)
No claim of novelty before the closest-prior-art table is complete. No claim of a "law" without a held-out confirmation.
No claim about UAVs/spacecraft. Every number in a paper/board must trace to a committed result file and a commit hash.
Exploratory and confirmatory results are labelled as such. Negative and null results are reported.
