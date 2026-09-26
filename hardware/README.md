# hardware/

The physical research platform — the validation instrument, not the scientific novelty by itself.

- `system_architecture.md` — the whole-system diagram and separation of concerns.
- `flight_controller/` — the mature, off-the-shelf flight-control platform (do not develop a novel
  flight controller unless it becomes scientifically necessary).
- `companion_computer/` — onboard compute running AeroNet's autonomy stack.
- `sensing/` — physical sensor documentation (calibration, uncertainty, limitations).
- `communications/` — the research communication link, independent from the flight-critical link.
- `mechanical/` — airframe, mounting, payload integration.
- `power/` — power architecture and monitoring.
- `ground_truth/` — the independent system used to determine true aircraft position; **the swarm
  must never validate itself using its own estimate.**
- `integration/` — how all of the above fit together and are checked as a system.
- `test_procedures/` — defined procedures for every bench/flight test.

All physical work must be supervised and compliant with relevant school, laboratory and aviation
requirements — see `competition/documentation/` for safety/ethics/approval records.
