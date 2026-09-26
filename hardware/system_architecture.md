# System Architecture

## Diagram

```text
Aircraft
    |
Flight controller
    |
Companion computer
    |
AeroNet autonomy
    |
Sensors
    |
Research communications
    |
Logging
    |
Ground truth
```

## Separation of concerns
Clearly separate, in both hardware and documentation:

- **Flight-critical systems** — anything needed to keep the aircraft safely airborne.
- **Research systems** — AeroNet's autonomy stack, sensing, and communication under test.
- **Measurement systems** — logging and ground truth, used only to record what happened, never to
  control the aircraft.

> _Expand this diagram with the actual hardware model numbers and interfaces once selected._
