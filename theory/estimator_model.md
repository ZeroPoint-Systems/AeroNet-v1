# Estimator Model

The estimator must be independently testable, do not hide it inside a controller.

## Define

- Local estimator
- Distributed estimator
- Consensus / fusion mechanism
- Uncertainty representation
- Measurement update
- Prediction update
- Communication update
- Failure handling

## Interfaces
> _Define the exact inputs/outputs of the estimator module so it can be swapped and tested in
> isolation (see `algorithms/estimators/` and `simulation/estimation/`)._

## Validation plan
> _How will this estimator be validated against ground truth before being trusted in an
> experiment? (see `simulation/validation/`)_
