AeroNet

Critical Information Boundaries in Decentralised Collective Autonomy
Information Limited State Estimation and Adaptive Reconfiguration in Infrastructure Free UAV Swarms

What AeroNet is

AeroNet is a research programme investigating whether a decentralised swarm of autonomous agents has a critical information boundary separating conditions under which the swarm can maintain a stable collective estimate from conditions under which that estimate becomes unreliable or unstable.

The project asks whether this boundary emerges from the interaction of sensing quality, sensing availability, communication capacity, communication reliability, communication latency, physical geometry, network topology, agent availability, estimation uncertainty and environmental conditions.

It then investigates whether the swarm can use only locally available information to recognise deteriorating information conditions and physically reconfigure itself to acquire better information.

The fundamental idea is that a decentralised swarm does not merely move through an environment while performing computation elsewhere. Its physical configuration can itself become part of the computation, by changing what information the swarm is able to obtain.

The project therefore connects sensing, communication, estimation, geometry, movement and agent availability into one experimentally measurable information limited system.

The UAVs are the physical experimental platform. The scientific subject is decentralised collective estimation under constrained information.

The central scientific problem

A distributed swarm has no single agent with complete knowledge. Each agent has incomplete observations, noisy measurements, limited communication, incomplete knowledge of other agents, finite computational resources, imperfect geometry, and potentially missing or failed neighbours.

Yet the group may still need to estimate some common state, for example the location or state of an external source.

The question is therefore not simply whether a swarm can estimate something, since that is already well studied. The deeper question is how much usable information the swarm needs before collective estimation becomes unstable, and whether the swarm can autonomously change its own sensing, communication and physical configuration to remain on the stable side of that boundary. That is the scientific core of AeroNet.

The primary research question

Does a critical information boundary exist between stable and unstable collective state estimation in a fully decentralised UAV swarm, how is that boundary determined by sensing, communication, physical geometry and agent availability, and can local information driven reconfiguration shift the boundary.

This is the formal research question. A shorter version, useful for presentations, is: does a critical information boundary exist in decentralised collective estimation, how does it scale with sensing, communication, geometry and agent availability, and can autonomous information allocation shift it.

What AeroNet is actually trying to discover

The project is trying to determine whether there is a reproducible operating boundary between two regimes, stable estimation and unstable estimation. The exact shape of this boundary is unknown. It may not be a simple line. It may instead be a multidimensional surface, expressed conceptually as a function of sensing, communication, geometry, noise, packet loss, latency, agent availability and swarm size.

The research question is whether such a boundary can be empirically identified and whether its position can be changed by adaptive collective behaviour.

The key distinction

AeroNet is not primarily asking whether adaptive swarm control improves performance, since that alone would be too ordinary a question. The deeper sequence is: does a critical information boundary exist, what determines that boundary, can it be measured, does it scale predictably, what causes the swarm to cross it, can the swarm detect that it is approaching the boundary, can it change its information conditions, and does that physically move the boundary.

The adaptive controller is therefore not the starting point of the project. It is the response to the scientific phenomenon discovered in the first part of the work.

The central conceptual idea, movement as information acquisition

Suppose a swarm's collective estimate is deteriorating. A conventional system might respond by increasing communication, increasing sensing, changing its estimator, or waiting for more information. AeroNet asks whether the swarm can instead recognise that its physical configuration itself is limiting information, and change that configuration so that future measurements become more informative.

Conceptually, poor information leads to increasing uncertainty, local agents detect the deteriorating information conditions, agents reconfigure, geometry changes, future observations improve, information increases, and collective uncertainty decreases.

This is what is meant by movement becomes computation. The movement is not merely executing a navigation command. The movement changes the information available to the collective system.

The overarching scientific hypothesis

A decentralised multi agent system operating under constrained sensing and communication possesses a reproducible information boundary separating stable and unstable collective estimation, and local information driven reconfiguration can shift that boundary by changing the swarm's future information availability.

This contains several testable claims, set out in full in hypotheses.md.

What is novel about AeroNet

This is the current working novelty position, deliberately more cautious than claiming that nobody has done this. There is already extensive research in cooperative localisation, distributed estimation, multi robot observability, information driven exploration, communication aware planning, sensor scheduling, formation optimisation, active localisation, fault tolerant localisation, collective perception, multi agent reinforcement learning, swarm criticality and RF source seeking.

None of the following statements is novel by itself: that communication affects swarm performance, that movement can improve sensing, that geometry affects localisation, that adaptive communication can improve estimation, or that UAVs can collaboratively locate sources. Those areas are already established, and this must be confirmed and referenced properly in literature_review.md before any novelty claim is finalised.

The proposed scientific distinction

The potentially novel object is the combination of sensing, communication, geometry, agent availability and collective estimation, viewed through the lens of a measurable critical information boundary. The project then asks whether local information assessment, combined with adaptive sensing, adaptive communication and physical reconfiguration, can shift that boundary.

The strongest potential contribution is not that a smarter swarm has been built. It is that the information conditions governing the stability of decentralised collective estimation have been experimentally characterised, and that autonomous physical reconfiguration has been investigated as a means of altering those conditions.

The novelty hierarchy

At the lowest level of novelty are statements already well established in the literature, such as that UAVs can use information gain, that communication affects collective performance, that movement affects communication or sensing, that formation geometry affects estimation, and that adaptive communication improves distributed estimation.

At a moderate level of potential novelty sits a measurable critical boundary governing collective estimation under multiple information constraints considered together.

At a higher level of potential novelty sits a multidimensional information surface jointly incorporating sensing, communication, geometry and agent availability.

At the highest level of potential novelty sits a generalised, dimensionless information quantity that predicts the transition across different swarm sizes, different environments and different sensing modalities, together with evidence that a decentralised controller can shift the measured boundary rather than merely improve performance at a fixed operating point.

The final paper will claim only what the literature and the experiments actually support.

What AeroNet is not

AeroNet is not primarily a drone building project, a flight controller project, an RF engineering project, a search and rescue demonstration, a formation control demonstration, an artificial intelligence demonstration, a reinforcement learning demonstration, a mesh networking project, or a hardware competition project. Any of these may appear as components, but none of them is the central scientific contribution.

Role of the UAVs

The physical UAVs are the experimental platform. Their purpose is to introduce real world phenomena that a purely mathematical system does not capture, such as sensor imperfections, communication latency, packet loss, asynchronous operation, positioning uncertainty, actuator limitations, environmental disturbances, hardware heterogeneity and computational limitations.

The project proceeds from theory, to simulation, to prediction, to physical experiment, to a comparison between simulation and physical result, rather than building drones first and inventing the science afterwards.

Hardware philosophy

The project will use a mature, off the shelf low level flight control platform rather than attempting to invent a new flight controller. Research autonomy sits above a companion computer, which sits above sensors and research communications, which sit above the flight controller and the aircraft itself. The research contribution sits above the basic aircraft stabilisation layer, which keeps the scientific question tractable. Physical testing will be conducted only in appropriate supervised and approved environments.

Role of the simulator

The simulator is the principal scientific instrument during the first stages of the project. It must model the agents, the environment, sensing, communication, estimation, geometry and control, as set out in full in the simulation folder.

The first experiments

The project does not begin by testing the full AeroNet controller. It first establishes the underlying phenomenon, using a controlled system with fixed swarm size, fixed estimator, fixed geometry, fixed sensing and fixed communication policy, varying one information constraint at a time and measuring collective estimation error, before investigating interactions between constraints. The purpose is to determine whether the phenomenon exists independently of the proposed controller.

The experimental progression

The full programme proceeds through a simple baseline, sensing degradation, communication degradation, geometry variation, agent failure, combined constraints, boundary estimation, swarm size scaling, ablations, adversarial conditions, the AeroNet adaptive controller, a boundary shift experiment, and finally physical validation. The exact final sequence may change after the literature review and pilot experiments.

The role of RF

RF is a demanding and useful experimental substrate, but the intellectual hierarchy places information limited collective estimation first, the decentralised swarm second, the physical UAV system third, and RF as one test modality within that system, rather than treating RF source seeking as the starting point from which a UAV swarm and then AeroNet are derived. The former framing gives the project substantially broader scientific scope.

The theoretical endpoint

The strongest theoretical version of AeroNet would eventually produce a boundary condition expressed as a function of sensing information, communication capacity, geometry or topology, noise, packet loss, failed agent fraction and agent availability, set equal to zero. This is currently a candidate framework, not an established equation. The actual mathematical form must emerge from the literature, the theory, the simulation and the experimental evidence together, and is developed formally in theory/information_boundary.md.

The ultimate scientific question

Is there a measurable information limit to decentralised collective autonomy, and can a physical swarm autonomously change its own information conditions well enough to move that limit. That is AeroNet.

The four layers of AeroNet

Layer one, the fundamental phenomenon, asks whether the information boundary exists. Layer two, the mechanism, asks what determines the boundary. Layer three, the intervention, asks whether decentralised adaptive behaviour can shift the boundary. Layer four, physical validation, asks whether the phenomenon survives in a real multi UAV system.

The contribution if everything works

If the evidence supports the major hypotheses, AeroNet would provide a scientific characterisation of the measured boundary between stable and unstable decentralised collective estimation, a mechanistic explanation of how sensing, communication, geometry and agent availability interact to determine that boundary, a mathematical framework connecting information availability to collective estimation stability, a decentralised adaptive mechanism that responds to deteriorating information conditions, a physical interpretation showing that changing the swarm's configuration changes its future information availability, a scaling result describing how the boundary changes with swarm size, and a validation result connecting simulation predictions to a physical UAV system.

Final canonical statement

If asked what exactly is being researched, the answer is that AeroNet investigates whether decentralised multi agent systems possess a critical information boundary separating stable from unstable collective state estimation. The project studies how sensing, communication, geometry, network structure and agent availability jointly determine that boundary, and whether agents using only local information can autonomously reconfigure their sensing, communication and physical configuration to shift it. The phenomenon is first tested in a controlled mathematical and simulation framework, and its predictions are then validated experimentally using a physical multi UAV system.

Everything else in this repository exists to establish, test, falsify, explain or physically validate that statement.

Scope

AeroNet investigates decentralised collective estimation under constrained information, specifically whether a critical information boundary exists and whether local, information driven reconfiguration can shift it.

Outside the scope of AeroNet are building a general purpose autonomous UAV platform, developing a new low level flight controller, building a complete search and rescue product, and treating the project as fundamentally an RF engineering exercise.

Definitions

Decentralised means no agent has access to the complete state of the swarm or the environment, there is no central computer that collects all data and issues commands, and every decision is made using only information available locally to that agent through its own sensors and through direct communication with neighbours.

Collective estimation means the swarm, acting only through local computation and local communication, produces at each agent an estimate of some shared quantity of interest, without any single agent ever holding a complete, centrally fused picture.

Information is the quantity, still to be finalised in theory/information_boundary.md, that measures how much usable, locally accessible knowledge an agent or the collective holds about the state being estimated.

Sensing is the process by which an agent obtains a noisy, partial measurement related to the state being estimated, through its own onboard sensors.

Communication is the exchange of messages between agents over a constrained channel, subject to bandwidth, latency and packet loss limits.

Geometry is the physical arrangement of the agents in space, together with the network topology that arrangement induces.

Agent availability is the fraction of agents that are functioning and contributing to sensing, communication and estimation at a given time.

Information boundary is the set of information conditions, across sensing, communication, geometry and agent availability, at which collective estimation transitions from stable to unstable.

Stable estimation is collective estimation error and uncertainty that remain bounded over a defined observation window, with the exact bound to be fixed with reference to the literature and confirmed in pilot experiments.

Unstable estimation is collective estimation error or uncertainty that grows without bound, or that exceeds the stability threshold for longer than a defined recovery window.

Information allocation is the local decision an agent makes about how to divide its limited sensing, communication and movement resources in order to acquire or preserve information.

Reconfiguration is a deliberate change in the swarm's physical geometry, undertaken specifically to change future information availability, rather than for any other navigation purpose.

Research constraints

No central leader. No central estimator. No GPS dependency in the research condition. Local information only. Bounded communication. Measurable uncertainty. Reproducible experiments.

Primary scientific claim being tested

The claim under test is not that the boundary exists. The claim under test is that the experiment tests whether a reproducible critical information boundary exists. This distinction is deliberate and important, and must be preserved in every later document that references this research question.
