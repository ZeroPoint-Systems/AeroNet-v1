# AeroNet2

A rigorous, tested testbed for **budget-limited decentralised estimation over lossy, delayed networks**, with exact
delayed-measurement fusion, a family of communication policies sharing one budget pacer (clean ablations), validated
statistics, and a hardware node that runs the *same* code as the simulator.

> **Status:** research software. The simulator is validated against theory and brute force (23 tests). Scientific claims are
> *exploratory* until you freeze the pre-registration (docs/02), complete the literature check (docs/03) and run the hardware (docs/05).
> Read `docs/00_PROJECT_OVERVIEW.md` first, then `results/RESULTS.md`.

## Install and verify
```sh
pip install -e ".[dev]"      # numpy; dev: pytest, matplotlib
pytest                       # 23 tests, ~3 s
```

## Reproduce every result (≈ 12 min on one core)
```sh
cd experiments
python run_law.py 20          # exploratory mismatch sweep   (seeds 10000+)
python run_frontier.py 30     # frontier + ablation ladder   (seeds 20000+)
python make_report.py         # -> results/RESULTS.md, fig_law.png, fig_frontier.png, law_fit.json
python run_law_confirm.py 20  # held-out configs, predictions frozen from law_fit.json (seeds 30000+)
cd ../hardware && python run_loopback_demo.py   # 4-process UDP software-in-the-loop check
```
Seeds 40000–40999 are **reserved** for your pre-registered confirmatory run. Do not use them for tuning.

## Layout
| Path | What |
|---|---|
| `src/aeronet2/model.py` | scenario, dynamics, directional sensors, manoeuvre bursts |
| `src/aeronet2/network.py` | lossy/delayed/outage network, per-cause accounting, bytes |
| `src/aeronet2/fusion.py` | `InfoFilter` (exact fusion, retrodiction), `CIFilter` (baseline) |
| `src/aeronet2/policies.py` | periodic, random, innov, delta, voi_blind/open/fb/**psa**, ci_periodic, broadcast, none |
| `src/aeronet2/sim.py` | simulation loop, centralised bound, Riccati steady state |
| `src/aeronet2/stats.py` | paired bootstrap, sign-flip p, Holm, equivalence; refuses NaN |
| `experiments/` | law sweep, frontier/ablation, confirmatory run, auto-report |
| `hardware/` | UDP node, loopback demo, `tc netem` script |
| `docs/` | overview, plan, pre-registration, literature protocol, theory, hardware, repo migration, awards/interview |

## Policies in one line each
`periodic` fixed schedule • `random` paced coin flip • `innov` paced normalised innovation • `delta` paced send-on-delta •
`voi_blind` VoI assuming the receiver has my covariance • `voi_open` VoI with an inferred peer model, open loop •
`voi_fb` + gossip feedback • `voi_psa` + consistency inflation (**proposed**) • `ci_periodic` estimate sharing + covariance
intersection • `broadcast` information upper reference • `none` local filter only.

## Known limitations
Linear-Gaussian 2-D target; static ring/complete/line topology; i.i.d. link loss (plus radio outages); myopic VoI;
no consensus-KF/diffusion baseline yet; no theorem yet; no physical data yet; novelty not verified.
