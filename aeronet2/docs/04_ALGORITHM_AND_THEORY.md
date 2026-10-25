# 04 — Algorithm (PSA-VoI) and theory status

## 1. Model
Target `x_{k+1} = F x_k + w_k`, `w ~ N(0,Q)` (continuous white-noise-acceleration, constant velocity, 2-D).
Agent i measures `z_k^i = H x_k + v_k^i`, `H = [I 0]`, `v^i ~ N(0,R_i)`. `R_i` has constant determinant; `anisotropy`
changes only its *shape* (directional sensors, e.g. ranging along a line of sight). A message `i→j` is lost w.p. `p_ij`,
delayed 1–3 steps, and dropped if the receiver's radio is in outage. Budget: `B` packets per agent per horizon.
Mismatch regime: bursts of unmodelled acceleration (not in the filters' `Q`).

## 2. Exact fusion of shared measurements (`fusion.InfoFilter`)
Each message carries one time-stamped measurement `(origin, s, z)` plus a gossiped covariance. A receiver adds the
information contribution `(H^T R_o^{-1} H, H^T R_o^{-1} z)` at time `s`, **at most once per (origin, s)**, and replays the
filter over `s..t` (windowed retrodiction). **Proposition 1 (tested):** the resulting posterior equals the batch posterior
given the set of delivered measurements (max error 0.0 vs. brute force; see `test_infofilter_equals_batch...`).
There is no double counting, so no covariance-intersection conservatism; and with delivery gaps/reordering the result is exact.

## 3. PSA-VoI policy (`policies.AgentPolicy`, names `voi_open` → `voi_fb` → `voi_psa`)
Per step, agent i with budget left and radio up:
1. **Peer model.** For each neighbour j keep `P̂_j`: predict `F P̂ F^T + Q`, then apply j's *own* sensor update (sensor models are
   common knowledge) — a data-independent recursion. After i sends to j: `P̂_j ← P̂_j + p_ij (update(P̂_j; R_i) − P̂_j)` (expected effect).
2. **Feedback (voi_fb, voi_psa).** Every packet carries the sender's covariance; on receipt from j, reset `P̂_j` to the gossiped value
   propagated forward by the packet age. No ACK channel is needed.
3. **Consistency inflation (voi_psa).** Track `n̄ = EWMA(ν^T S^{-1} ν)` (normalised innovation squared; 2 when consistent).
   Use `c = max(1, n̄/2)` and score with `c·P̂_j` — the score rises when the model is wrong.
4. **Score.** `s = max_j p_ij · [tr_pos(P) − tr_pos(P − P_{:,pos}(P_pos+R_i)^{-1}P_{:,pos}^T)]` evaluated at `c·P̂_j`
   (expected reduction of the receiver's position-covariance trace from fusing i's measurement), receiver `= argmax`.
5. **Pacing.** Fire if `s > θ`; update `θ ← θ·exp(γ_n(1[fire] − r_t))` with decreasing gain `γ_n` and deadline-aware target
   rate `r_t = (B − sent)/(T − t)`. This hits the budget with no manual threshold and makes every scored policy comparable
   (same pacer, only the **score** differs — this is the ablation design).
Complexity per agent per step: `O(|N(i)|)` 2×2 solves + one 4×4 Riccati step per neighbour.

## 4. Theory status — be precise about what is and is not proven
- **Proposition 1** (exact delayed-measurement fusion): proven by construction, verified numerically.
- **Observation 2 (numerical, not a theorem):** with a correct model, an open-loop VoI schedule is as good as or better than the
  closed-loop policies tested; noise-like triggers are no better than periodic. Intuition: with exact fusion the error covariance
  depends only on *which* measurements are delivered, not on their values (the classical sensor-scheduling separation result).
  **Subtlety to resolve:** with *data-dependent* triggers the receiver could extract extra information from the *absence* of a message
  ("negative information"), which `InfoFilter` ignores; the Bayes-optimal estimator under such triggers is generally not linear-Gaussian.
  A rigorous statement therefore needs a defined trigger class — this is the first theory task.
- **Open problem 3 (mechanism of the mismatch gain):** conjecture that the gain equals the budget fraction that can be
  concentrated into episodes where the filter is inconsistent, giving a non-monotone dependence on duty cycle. Held-out data
  already rule out simple power laws (RESULTS.md §1, law_confirm.json).
- **Known limitations of PSA-VoI:** myopic (no multi-step lookahead); peer model ignores third-party information (pessimistic);
  assumes nominal link probabilities are known; consistency monitor is an EWMA, not a calibrated test; position-trace objective only.

## 5. Simulator validation evidence (all in `tests/`)
streams independent across seeds/agents • fusion = batch • duplicate/stale handling • centralised and local RMSE vs Riccati theory •
NEES consistent (≈4) • per-cause packet accounting • budget respected • outages block delivery • pacer hits rate at any score scale •
v1 "reactive" signal exceeds its threshold at the chi rate (i.e. is noise) • statistics refuse NaNs.
