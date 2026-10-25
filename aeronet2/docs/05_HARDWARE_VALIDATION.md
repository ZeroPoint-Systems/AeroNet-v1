# 05 — Physical validation protocol

Goal: show that the *simulated* behaviour (accuracy vs messages, null regime, mismatch regime) survives real sensors,
real clocks and a real network. Only claim what the hardware can support (networked embedded nodes, **not** UAV swarms).

## Rig (budget version)
- 4 nodes: Raspberry Pi / ESP32 + Wi-Fi (or 4 laptops for a first dry run). `hardware/node.py` is the reference node
  (runs on Pis as-is; port the `InfoFilter` maths to MicroPython only if you need ESP32).
- **Independent ground truth** (this is what makes it validation, not a demo):
  - Option A (best): a target on a motorised rail or turntable with encoder/stepper-count position, tracked by each node's
    own sensor (ultrasonic/ToF range, or a camera + ArUco marker).
  - Option B: overhead camera tracking an ArUco-tagged cart as reference; nodes use cheaper, noisier sensors.
  - Not acceptable as the main result: a synthetic signal inside the code (that is the loopback demo).
- Sensor model: measure each node's noise empirically (≥ 500 static samples) and put the measured R into the model.
  The target-motion model parameter `q` must also be fitted from reference data, not guessed.

## Time and network
- Clocks: run `chrony` against a LAN reference (or PTP). Log the measured offset before and after every run;
  one-way latency numbers are invalid without it. Alternative: round-trip echo timing, no sync needed.
- Real Wi-Fi is not repeatable. Use `hardware/netem_impair.sh` (Linux `tc netem`) to sweep loss ∈ {0,10,30}% and
  delay ∈ {10,50,150} ms on top of the natural network, and also record one run with *no* injected impairment.
- Fixed step rate (e.g. 10 Hz); each node logs per step: wall time, own measurement, estimate, covariance trace, packets sent/received,
  lateness of the step loop (to detect OS jitter).

## Experiments (pre-register before running)
1. **Calibration:** static target; measure R; check NIS ≈ expected (sensor model valid?).
2. **Null regime:** smooth target motion matching the model; policies {none, periodic, voi_open, voi_psa}; 10 repeats each.
3. **Mismatch regime:** the same plus scripted manoeuvres (rail speed/direction changes at random times).
4. **Impairment sweep:** loss × delay grid for periodic vs voi_psa at one budget.
5. **Sim-to-real:** re-run the simulator with the *measured* R, q, loss, delay; compare predicted vs measured RMSE and message counts.

## Analysis and success criteria (fix in advance)
- Primary: paired RMSE difference vs periodic per repeat (same trajectory), 95% bootstrap CI.
- Validation metric: |RMSE_sim − RMSE_hw| / RMSE_hw per condition; report the gap, explain residuals, do not hide them.
- Success = qualitative pattern reproduced (null regime: no detectable difference; mismatch regime: voi_psa better) **or** a
  clearly explained deviation. A failed replication is a valid, reportable result.

## Practical checklist
- Repeat each condition ≥ 10×; randomise condition order (avoid drift/time-of-day confounds).
- Keep raw logs, rig photos, wiring, firmware hashes, and git commit of the code used.
- Safety/regulatory: low-voltage electronics only; check the ISEF rules/forms that apply to your rig *before* building.
