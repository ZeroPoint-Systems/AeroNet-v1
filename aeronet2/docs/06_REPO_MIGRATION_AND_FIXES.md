# 06 — Migrating the repository and where each audit finding went

## Layout to adopt
```
AeroNet-v1/
  aeronet2/            <- this package (canonical; `pip install -e aeronet2`)
  archive/             <- everything old, untouched, with archive/README.md explaining status
      simulation/ aeronet_research/ aeronet_research_v1/ experiments_legacy/ (lab_v1..v7, master_key, runtime)
  docs/ (move aeronet2/docs/* here)   research journal/ (dated entries)
  README.md            <- rewrite: one question, one codebase, status table that matches reality
```
```sh
git checkout -b revamp
mkdir archive && git mv simulation aeronet_research aeronet_research_v1 archive/
git mv experiments archive/experiments_legacy      # lab_v1..v7, master_key, scientific, runtime
git rm --cached repository_tree.txt aeronet_*.txt   # source dumps; also contains your local Windows path
# copy aeronet2/ into the repo root, commit, then:  pip install -e aeronet2 && pytest aeronet2
```
Write `archive/README.md`: "Exploratory prototypes, superseded; results from these are **not** evidence. See aeronet2."

## Audit finding → resolution
| # | Finding | Resolution in aeronet2 | Status |
|---|---|---|---|
| 1 | Measurement noise streams overlap across seeds (35 of 180) | `rng.py` SeedSequence streams; test asserts 180 distinct | Fixed + tested |
| 2 | Peer states not time-aligned (stale bias) | Exact retrodiction fusion of time-stamped measurements | Fixed + tested vs batch |
| 3 | Reactive/predictive triggers were noise; budget exhausted by step ~141 | Shared deadline-aware pacer; score is the only difference; test shows v1 signal = chi rate | Fixed + tested |
| 4 | Warning metric had zero skill (recall = FPR) | Removed; not used | Dropped |
| 5 | Heuristic fixed-gain consensus, no covariance | Exact information-form fusion; CI baseline implemented separately | Replaced |
| 6 | "10% loss" but 31% undelivered; lumped accounting | Per-cause accounting (channel / outage / horizon); invariant tested | Fixed + tested |
| 7 | Identical agents, nothing complementary | Anisotropic directional sensors at constant information volume; knob `anisotropy`, `sensor_spread` | Added |
| 8–9 | Many codebases; README ≠ reality | Single canonical package; migration above | **You must do the repo move + README** |
| 10 | Research-question drift | One lead RQ (00) | Decided; **you must confirm** |
| 11 | "Pre-registered" but templates empty; post-hoc fixes | 02: lineage + template; confirmatory seeds reserved | **You must fill + tag** |
| 12 | `aeronet_runtime` (fixed "adaptive", sleep timing, sender-side loss) | `hardware/node.py`: same filter/policy code as sim, barrier start, step-clocked, logs lateness, netem for impairments | Replaced; **needs real-device runs** |
| 13 | Metrics: pooled RMSE, no consistency/trade-off | Steady-state RMSE, NEES, frontier over budgets, gap-closed, bytes incl. covariance | Fixed |
| 14 | Bytes counted only the state vector | Header + payload + gossip covariance counted | Fixed |
| 15–16 | Tiny effects, weak/invalid CIs; NaNs silently dropped | `stats.py`: paired bootstrap, sign-flip p, Holm, equivalence margins; raises on NaN | Fixed + tested |
| 17 | Tests didn't check correctness | 23 tests: theory match, batch equality, consistency, accounting | Fixed |
| 18–19 | Unused `network_radius`; availability semantics differ | Removed; outage = radio down only (sensing continues) — documented | Fixed |
| 20–23 | Crash path, `inv`, non-Joseph, step-0 send | Crash path gone (no `NotImplementedError` stubs); Joseph form in `CIFilter`; `solve` in covariance updates; information-form inversions are symmetrised; periodic offsets staggered (scored policies may still send at step 0) | Mostly fixed |
| 24 | Repo hygiene (UTF-16 dumps, local path, empty changelog) | Commands above; write a real CHANGELOG | **You must do** |
Open items not solved by code: literature review, theory, hardware data, ownership/understanding, mentor.
