# algorithms/aeronet/

The actual AeroNet algorithm, split into independently testable components:

- `information_state/`
- `local_information_assessment/`
- `action_selection/`
- `reconfiguration/`
- `communication_policy/`
- `sensing_policy/`
- `recovery_policy/`

**Key principle:** AeroNet must operate using only locally available information. Do not
accidentally give it global knowledge that the baseline systems do not receive (see
`CONTRIBUTING.md`, Rule 9).
