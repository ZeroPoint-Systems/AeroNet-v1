# Falsification Tests

This file actively tries to destroy the central hypotheses. For every test below, specify:

```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT1, No boundary exists
```text
Claim being tested: A reproducible boundary exists (H1).
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT2, Boundary is caused only by connectivity
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT3, Boundary is caused only by sensing
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT4, Boundary is caused only by estimator choice
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT5, Boundary is a finite-size effect
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT6, Boundary disappears with more agents
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT7, Boundary disappears with fewer agents
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT8, Boundary changes with topology
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT9, Boundary is an RF-specific phenomenon
```text
Claim being tested: The effect is a general information limitation, not specific to RF sensing (H8).
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT10, Boundary is caused by simulator artefacts
```text
Claim being tested:
Experiment: (see simulation/validation/)
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT11, Boundary is caused by numerical instability
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT12, Boundary disappears with realistic latency
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT13, Boundary disappears under sensor bias
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT14, Boundary disappears under asynchronous operation
```text
Claim being tested:
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT15, Adaptive controller only improves average performance (does not shift the boundary)
```text
Claim being tested: H6, adaptive allocation shifts the operating boundary, vs. it merely improves
average-case performance within the existing boundary.
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT16, Adaptive controller genuinely shifts the boundary
```text
Claim being tested: H6.
Experiment:
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```

## FT17, Physical system does not reproduce simulation
```text
Claim being tested: Simulation predictions transfer to the physical platform.
Experiment: (see experiments/hardware_validation/)
Expected result if hypothesis is correct:
Expected result if hypothesis is wrong:
Interpretation:
```
