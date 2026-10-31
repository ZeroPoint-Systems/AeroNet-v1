# CDIA work status (resume point)

Branch `cdia-cycle1` (local, based on `revamp` b3a6b3e). Nothing committed, nothing pushed.

## Cycle 1 outcome
CDIA as specified shows no demonstrable advantage in the main scenario (see `docs/CDIA_CYCLE1_REPORT.md`).
Headroom diagnostic: even hindsight oracles gain only about 0.2 points of decision error, below what 30 seeds resolve.

## Seeds
- 1000-1009: pilot (scenario fixed from it). Used.
- 2000-2029: main run and headroom diagnostic. Used.
- 3000-3019: held-out plan in `run_cdia.py`. NOT used. Reserved for a revised algorithm in a scenario with headroom.
- Use 4000-4029 for any revised validation run.

## Next (cycle 2), in order
1. Find a scenario with measurable headroom: raise the oracle-to-periodic gap above 20% relative before running any policy comparison.
2. Test the persistence hypothesis: the one-step decision value ignores that a shared measurement keeps improving later estimates (small process noise). Derive a horizon-aware value and check it against the oracle.
3. Add correlated sensor noise (common-mode error) and a corresponding filter, then the compute action.
4. Implement a published distributed baseline (consensus plus innovations) under the same budget.
