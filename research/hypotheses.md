Hypotheses

The overarching hypothesis is that a decentralised multi agent system operating under constrained sensing and communication possesses a reproducible information boundary separating stable and unstable collective estimation, and that local information driven reconfiguration can shift that boundary by changing the swarm's future information availability. This overarching hypothesis contains the eight testable claims set out below, together with three null hypotheses.

For every hypothesis, the following fields are recorded once the relevant theory and literature work is complete: rationale, independent variables, dependent variables, predicted relationship, expected observation, falsifying observation, required experiment and analysis method. Where a field cannot yet be filled in honestly, it is marked accordingly rather than guessed.

H1, a critical information boundary exists

Statement. A reproducible boundary exists between stable and unstable collective estimation under constrained information.

What this means. As information availability is progressively reduced, the swarm should not simply experience an arbitrary, gradual degradation. There may instead be a region where collective estimation changes regime.

Evidence supporting H1. Repeated experiments identify a consistent transition between bounded, stable estimation and unstable or unacceptable estimation.

Evidence against H1. Performance changes smoothly with no reproducible transition, or the apparent transition disappears under appropriate controls.

Rationale. LITERATURE REQUIRED, to be completed once literature_review.md has established what is already known about thresholds and transitions in cooperative estimation and multi agent observability.

Independent variables. The information conditions being varied, drawn from sensing quality, communication capacity, geometry and agent availability, with exact levels fixed in experimental_protocol.md.

Dependent variables. Collective estimation error and estimation uncertainty, measured against ground truth, with the exact primary metric fixed in variables.md.

Predicted relationship. A narrow region of information conditions over which the probability of stable estimation falls sharply, rather than a gradual decline across the whole range tested.

Expected observation. A repeatable, statistically distinguishable transition region, consistent across independent replicates and random seeds.

Falsifying observation. No repeatable transition is found, or performance declines smoothly and continuously across the full range of conditions tested, with no narrow transition region.

Required experiment. The phenomenon test described in experimental_protocol.md, prior to any adaptive controller being introduced.

Analysis method. Boundary estimation as set out in analysis/boundary_estimation, including a statistical test for sharpness of transition rather than a purely visual judgement.

H2, the boundary is multidimensional

Statement. The boundary depends jointly on sensing quality, communication capacity, geometry and agent availability, rather than on any single variable in isolation.

Rationale. Better sensing may compensate for poor communication, better geometry may compensate for weaker sensing, and additional agents may increase available information while also increasing communication burden, so the relevant object is potentially a joint information condition rather than a single critical threshold such as a critical communication rate.

Independent variables. Sensing quality, communication capacity, geometry, agent availability, noise, packet loss, latency and swarm size, varied both individually and in combination.

Dependent variables. As for H1.

Predicted relationship. Interaction effects between at least two of the four principal factors, such that the boundary in one variable shifts depending on the level of another.

Expected observation. Statistically significant interaction terms in the analysis described in analysis/statistics, rather than purely additive effects.

Falsifying observation. The four factors affect the boundary independently and additively, with no meaningful interaction terms, in which case the boundary can be treated as separable.

Required experiment. A factorial sweep across the four principal factors, as set out in experimental_protocol.md.

Analysis method. Regression with interaction terms, as set out in analysis/statistics.

H3, information degradation drives instability

Statement. Reduced information availability increases estimation instability.

Rationale. This is the most direct test that the proposed information conditions, rather than some unrelated factor, are actually responsible for changes in estimation quality.

Independent variables. Sensor noise, sensor availability, sensor update rate, communication rate, packet loss, latency, topology, geometry and agent availability, each varied under experimental control.

Dependent variables. As for H1.

Predicted relationship. A monotonic increase in instability as information availability is reduced, at least within the region away from the boundary itself.

Expected observation. A consistent direction of effect across repeated trials as each information source is degraded in turn.

Falsifying observation. Reducing information availability does not increase instability, or the observed increase in instability can be fully explained by connectivity loss alone, which is addressed directly under the alternative explanations in falsification_tests.md.

Required experiment. Sensing degradation and communication degradation experiments, as set out in experimental_protocol.md.

Analysis method. As for H1, together with the specific alternative explanation test described in falsification_tests.md.

H4, physical configuration affects future information

Statement. Physical repositioning can increase future information availability.

Rationale. If geometry affects observation quality, observability, communication connectivity and measurement diversity, then geometry is an information variable rather than merely a formation control variable, and movement can be understood as an action that changes the information state rather than only the position state.

Independent variables. Swarm geometry and configuration, and the movement policy used to change it.

Dependent variables. Information gain or the chosen information metric, estimation uncertainty, and movement cost.

Predicted relationship. Certain geometric changes increase future information availability by more than the movement cost required to achieve them, at least under some information conditions.

Expected observation. A measurable improvement in the information metric following a deliberate reconfiguration, that exceeds the improvement seen under an equivalent random movement of the same cost.

Falsifying observation. Reconfiguration produces no measurable improvement in information availability beyond that of random movement of equal cost, or the movement cost exceeds any benefit under all conditions tested.

Required experiment. Geometry variation experiments, as set out in experimental_protocol.md.

Analysis method. Comparison of information gain per unit movement cost across geometries, as set out in analysis/metrics.

H5, the swarm can recognise deteriorating information

Statement. A decentralised controller can detect deteriorating information conditions using local information.

Rationale. For the system to remain genuinely decentralised, each agent must determine, from its own locally available information alone, whether the collective is approaching an information limited regime, without access to hidden global information.

Independent variables. The local information available to the controller, and the true, but not locally visible, information condition of the swarm as tracked by the simulator for evaluation purposes only.

Dependent variables. Detection accuracy and detection latency, that is, how reliably and how quickly the local controller's assessment matches the true underlying condition.

Predicted relationship. Detection accuracy and latency that are adequate for the controller to act before the swarm crosses into the unstable regime, under at least some of the conditions tested.

Expected observation. The local detector's assessment correlates meaningfully with the true information condition, measured only for evaluation and never fed back into the controller itself.

Falsifying observation. The local controller cannot distinguish deteriorating from stable conditions using only locally available information, or can only do so with a detection latency too long to allow useful action.

Required experiment. A detection accuracy and latency study, prior to full closed loop control experiments, as set out in experimental_protocol.md.

Analysis method. Signal detection style analysis, as set out in analysis/metrics and analysis/statistics.

H6, the swarm can shift the boundary

Statement. Adaptive information allocation can shift the operating boundary.

Rationale. This is the major control hypothesis. The question is not whether AeroNet produces lower average error, but whether adaptive information allocation allows stable collective estimation under conditions that previously produced instability, which would mean the operating boundary itself has moved, rather than only average case performance having improved at a fixed operating point.

Independent variables. Controller type, that is, a fixed static policy against the adaptive AeroNet policy, together with the information conditions swept across the boundary region.

Dependent variables. The estimated boundary location under each controller, using the same boundary estimation method as H1.

Predicted relationship. The boundary estimated under the adaptive policy lies at a strictly more difficult information condition than the boundary estimated under the best matched static policy.

Expected observation. A statistically significant difference between the two estimated boundaries, not merely a difference in average error at a single fixed condition.

Falsifying observation. The adaptive controller reduces average error at fixed conditions but does not shift the estimated boundary relative to the best matched static baseline, or the boundary shift disappears once the strongest available baseline is used for comparison.

Required experiment. The boundary shift experiment, as set out in experimental_protocol.md, following the phenomenon test and baseline experiments.

Analysis method. Boundary estimation and comparison, as set out in analysis/boundary_estimation, with the two possibilities, a genuine boundary shift against an average performance improvement, explicitly distinguished as described in the AeroNet controller documentation.

H7, the boundary scales with swarm size

Statement. The boundary changes predictably with swarm size and topology.

Rationale. Increasing the number of agents may increase available information but also increases communication burden, so there may be a predictable relationship, and possibly a normalised quantity that allows results from different swarm sizes to be compared directly.

Independent variables. Swarm size N, with candidate values such as two, four, eight and sixteen agents, the final values to be justified experimentally and computationally rather than assumed, and network topology.

Dependent variables. As for H1, together with the estimated boundary location as a function of N.

Predicted relationship. A systematic, ideally monotonic, relationship between N and the boundary location, which may or may not collapse onto a single curve once appropriately normalised.

Expected observation. A consistent trend in boundary location across the tested values of N, replicated across independent runs.

Falsifying observation. No consistent relationship between N and the boundary location, or the relationship is dominated by finite size artefacts that disappear at larger N, which is addressed directly in falsification_tests.md.

Required experiment. The swarm size scaling experiment, as set out in experimental_protocol.md.

Analysis method. Scaling analysis, as set out in analysis/scaling_analysis and theory/scaling_model.md.

H8, the phenomenon is not merely an RF artefact

Statement. The observed phenomenon should not depend exclusively on one sensing modality if it represents a general information limitation.

Rationale. RF is a useful and demanding experimental substrate, but AeroNet should not narrow to a better RF source seeking algorithm. If the same fundamental behaviour appears under another sensing modality, that strengthens the claim that the phenomenon is general. If it does not, that is also a scientifically important result, and must be reported honestly rather than set aside.

Independent variables. Sensing modality, with RF as the first modality and at least one alternative modality to be chosen once the literature review and simulator design are complete.

Dependent variables. As for H1, compared across modalities using the same information metric.

Predicted relationship. A boundary of broadly similar qualitative character across modalities, though not necessarily at the same numerical values.

Expected observation. A reproducible boundary under the alternative modality as well as under RF, with the same qualitative dependence on sensing, communication, geometry and agent availability.

Falsifying observation. The boundary, or the phenomenon itself, appears only under RF and not under the alternative modality tested, in which case the phenomenon must be described as modality specific rather than general.

Required experiment. Repetition of the phenomenon test and boundary estimation experiments under an alternative sensing modality.

Analysis method. As for H1, applied separately to each modality and then compared.

Null hypotheses

H0-1. No reproducible critical boundary exists.

H0-2. Adaptive reconfiguration does not shift the boundary relative to matched static policies.

H0-3. Observed transitions are explainable entirely by connectivity loss rather than collective information insufficiency.

Dependencies between hypotheses

H2 through H8 presuppose H1, since there is nothing to characterise, shift or scale if no boundary exists in the first place. H6 presupposes H5, since a controller cannot usefully act on deteriorating information conditions that it cannot detect. H7 and H8 are tests of the generality of whatever boundary is found under H1 and H2, and do not depend on H4, H5 or H6 succeeding. If H1 is falsified, H2 through H7 are moot and the project must report that no boundary was found, rather than continuing to test properties of a boundary that does not exist.
