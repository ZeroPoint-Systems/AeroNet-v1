# Mathematical Framework

Define the entire system mathematically, once, here. Define notation in this file and reuse it
consistently in every other `theory/` document, in code comments, and in the papers, do not
redefine symbols elsewhere.

## Components to define

### Swarm state
> _Notation and definition for the joint state of all agents._

### Individual agent state
> _Notation and definition for a single agent's state (position, velocity, heading, etc.)._

### Environmental state
> _Notation for whatever the swarm is trying to estimate (target/source location, field, etc.)._

### Observation model
> _How an agent's measurement relates to the true state, including noise._

### Communication graph
> _Notation for the (possibly time-varying, possibly directed) inter-agent communication graph._

### Estimator
> _Notation for each agent's local estimate and its uncertainty representation._

### Control policy
> _Notation for the mapping from local information to action (movement, sensing, communication)._

### Information state
> _Notation for whatever quantity is proposed to summarise "how much information" is available._

### Uncertainty
> _Notation for how estimation uncertainty is represented and propagated._

### Resource constraints
> _Notation for bandwidth, energy, and any other bounded resource._

## Notation table

| Symbol | Meaning | Units | Defined in |
|---|---|---|---|
| | | | |

Keep this table updated as new symbols are introduced anywhere in `theory/`.
