# analysis/

Converts raw measurements into scientific evidence.

- `preprocessing/` — cleaning, synchronisation, unit conversion, quality control, missing-data
  handling. Never silently delete data.
- `metrics/` — every metric defined mathematically (name, definition, equation, units,
  interpretation, limitations).
- `statistics/` — confidence intervals, effect sizes, hypothesis tests where appropriate, bootstrap
  procedures, regression, mixed-effects models where appropriate, multiple-comparison handling,
  power/sample-size reasoning. Do not just report p-values.
- `boundary_estimation/` — the core analysis: where stability holds, where it fails, how the
  transition changes, how uncertain the boundary estimate is. Only call it a "phase transition" if
  the evidence actually supports that interpretation.
- `visualisation/` — every figure used in a paper must be reproducible from code here. No manually
  edited scientific graphs.
- `ablation_analysis/` — which components actually matter.
- `scaling_analysis/` — whether results generalise with swarm size.
- `hardware_comparison/` — simulation prediction vs. physical result vs. prediction error;
  disagreement is not hidden.
- `reproducibility/` — one-command or fully documented workflows to rebuild datasets, rerun
  analysis, and regenerate every figure and table.
