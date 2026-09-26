# algorithms/

Implementations of every algorithm being compared, kept strictly separate so results are
attributable.

- `baselines/` — every serious baseline (see below); never mixed with AeroNet's own code.
- `aeronet/` — the actual AeroNet algorithm.
- `estimators/` — every estimator implementation.
- `information/` — information-theoretic metrics.
- `communication/` — communication policies.
- `controllers/` — research-level movement/control logic (keep low-level aircraft stabilisation
  in `hardware/flight_controller/`, not here).

**Rule 9 (see `CONTRIBUTING.md`): do not give AeroNet information that the real decentralised
system would not possess.** The AeroNet algorithm must operate on local information only — do not
accidentally wire in global knowledge that baselines don't get either.
