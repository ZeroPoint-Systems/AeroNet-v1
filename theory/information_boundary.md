# Information Boundary

This is the central theoretical document for AeroNet.

## Candidate information state
> _Define a candidate information state, e.g. `I(t)`, or an equivalent mathematically defensible
> quantity, using the notation from `mathematical_framework.md`._

## Relationships to investigate
Investigate relationships between:

- information acquisition
- information loss
- estimation uncertainty
- communication
- sensing
- geometry
- agent availability

## Candidate boundary condition

```text
B(S, C, G, N, P, F, N_agents) = 0
```

Where `S` = sensing quality, `C` = communication capacity, `G` = geometry, `N` = noise level,
`P` = packet loss / latency, `F` = agent failure fraction, `N_agents` = swarm size.

> **Do not assume this exact functional form is correct.** Treat it as a candidate model to test,
> not a conclusion.

## Questions this document must answer

- What would constitute evidence *for* a boundary?
- What would constitute evidence *against* one?
- What mathematical properties should the boundary have (continuity, monotonicity in each
  argument, symmetry, scaling behaviour)?

## Relationship to falsification tests
Cross-reference each property/claim above with the corresponding test in
`research/falsification_tests.md`.
