# 03 — Literature review protocol and novelty ladder

**Status: NOT DONE.** Nothing in this package establishes novelty. The titles below come from the author's
background knowledge and **must be looked up and verified (existence, authors, year, what they actually prove)**
before they are cited anywhere. Treat this file as a reading list and a search plan, not as a bibliography.

## 1. Search protocol (do this first, ~2 weeks, log every query)
- Sources: Google Scholar, IEEE Xplore, arXiv (eess.SY, cs.MA, stat.ML), ScienceDirect (Automatica, Signal Processing).
- Query families (record date, query, #results screened, papers kept):
  - "event-triggered state estimation" / "send-on-delta" / "variance-based triggering"
  - "distributed Kalman filter" + "packet loss" / "communication delay" / "limited bandwidth"
  - "consensus + innovations", "diffusion Kalman filter", "covariance intersection" + "delayed"
  - "sensor scheduling" + "periodic optimal", "offline schedule" + "Kalman" + "event-triggered"
  - "out-of-sequence measurement" + "distributed"; "model mismatch" + "event-triggered" + "NIS"
  - "value of information" + "communication" + "multi-agent estimation"
- Snowball: for each of the 10 most relevant papers, read the reference list and the "cited by" list.
- Output: a **closest-prior-art table** (paper | setting | policy | fusion | theory | what it does NOT cover).

## 2. Reading list to verify (from memory — may contain errors)
| Topic | Candidate reference | Why it matters here |
|---|---|---|
| Intermittent observations, critical arrival rate | Sinopoli, Schenato, et al., "Kalman filtering with intermittent observations", IEEE TAC, 2004 | Classical "boundary" result for centralised unstable systems |
| Offline-optimal measurement schedules | Meier, Peschon, Dressler, "Optimal control of measurement subsystems", IEEE TAC, 1967 (and later sensor-scheduling literature) | Separation: for linear-Gaussian MSE the best schedule is data-independent. This is what Experiment F rediscovers numerically |
| Event-based estimation | Trimpe & D'Andrea, "Event-based state estimation with variance-based triggering", IEEE TAC, 2014 | Closest to a covariance-aware trigger |
| Rate/quality trade-off | Wu, Johansson, et al., "Event-based sensor data scheduling: trade-off between communication rate and estimation quality", IEEE TAC, 2013 | Frontier framing |
| Stochastic triggers | Han, Mo, Wu, et al., "Stochastic event-triggered sensor schedule for remote state estimation", IEEE TAC, 2015 | Randomised triggering vs deterministic |
| Distributed KF | Olfati-Saber, "Distributed Kalman filtering for sensor networks", CDC 2007 | Standard consensus-KF baseline (not yet implemented here) |
| Consensus + innovations | Kar, Moura, et al. (2010s) | Distributed estimation with imperfect communication |
| Covariance intersection | Julier & Uhlmann, 1997 | Implemented as `ci_periodic` baseline |
| Out-of-sequence measurements | Bar-Shalom, "Update with out-of-sequence measurements in tracking: exact solution", IEEE TAES, 2002 | Same family as the retrodiction in `InfoFilter` |

## 3. Novelty ladder — claim only the highest rung that survives the literature check
1. **Engineering / reproducibility contribution (safe):** an open, tested testbed with exact delayed-measurement fusion,
   per-cause packet accounting, common-random-number comparisons, theory-validated simulator.
2. **Empirical characterisation (probable):** a decomposition of *where* adaptive communication helps in lossy decentralised
   estimation — null regime (calibrated model: no policy detectably beats a good offline schedule), mismatch regime
   (gain from consistency-aware triggering), and the budget range where peer-state awareness adds value.
3. **Method (possible, unverified):** PSA-VoI = consistency-inflated, peer-state-aware value-of-information triggering with
   gossip-based peer inference and deadline-aware quantile pacing. The *components* are individually known ideas
   (VoI scheduling, NIS monitoring, budget pacing). A claim of novelty can only rest on the **combination**, the
   **ablation evidence**, and **absence from the closest-prior-art table**.
4. **Law (not established):** a predictive law for the adaptive gain. The exploratory fit is weak (see RESULTS.md,
   confirmatory section). Do not call it a law unless held-out configurations confirm it.

**Fallback rule:** if the prior-art table contains a paper that already reports a mismatch-driven triggering gain with a
comparable decomposition, the project narrows to rung 1–2 and says so. That is still an honest, defensible project.
