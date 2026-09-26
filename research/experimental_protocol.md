# Experimental Protocol

This defines exactly how the experiment will be conducted, written before seeing the final
results. Someone else should be able to read this file alone and reconstruct the experiment.

## Experimental objective
> _State the objective this protocol serves, tie it back to a hypothesis ID in `hypotheses.md`._

## Experimental units
> _What constitutes one experiment (one run, one trial, one scenario instance)?_

## Experimental factors
Example factor set, finalise the actual list before running anything:

```text
N (swarm size)
sensing uncertainty
sensing rate
communication rate
packet loss
latency
network topology
agent failure
geometry
environmental disturbance
```

## Experimental levels
Specify exact levels before seeing results. Example:

```text
N = 2, 4, 8, 16
```

> _Do not choose levels after seeing results._

## Primary endpoint
> _Choose ONE primary measure of collective estimation performance._

## Secondary endpoints
> _Define everything else measured but not treated as primary._

## Randomisation
> _Define random seeds and scenario generation procedure._

## Replication
> _Specify the number of independent repetitions per condition._

## Stopping conditions
> _Define exactly when a single experiment run ends._

## Data recording
> _Define every field logged, at what rate, and in what format._

## Exclusion criteria
> _Define, in advance, when data can legitimately be excluded._

## Statistical analysis
> _Specify the intended analysis method before the main campaign runs (see `analysis/statistics/`)._

## Boundary estimation
> _Define exactly how the critical boundary will be estimated from the data (see `analysis/boundary_estimation/`)._

## Physical validation
> _Define exactly which simulation prediction will be tested physically, and how success/failure
> of that prediction will be judged._

## Reproducibility checklist
- [ ] Random seeds recorded
- [ ] Configuration files versioned
- [ ] Code version (git commit) recorded per run
- [ ] Raw data left immutable
- [ ] Protocol frozen and dated before main campaign
