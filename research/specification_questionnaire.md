AeroNet master research specification questionnaire, answered

This document answers, in order, every question in the AeroNet master research specification questionnaire. Where an answer is genuinely settled it is marked DECIDED. Where it depends on the literature review it is marked LITERATURE REQUIRED. Where it can only be settled by a small pilot run it is marked PILOT REQUIRED. Where it can only be settled by the main experimental campaign it is marked EXPERIMENT REQUIRED. Where it is simply not yet known it is marked UNKNOWN. Where a question does not apply to AeroNet it is marked NOT APPLICABLE. No answer has been chosen because it makes AeroNet sound more novel than the evidence currently supports.

Part I, core research question

1. What is the exact primary research question. DECIDED. Does a critical information boundary exist between stable and unstable collective state estimation in a fully decentralised UAV swarm, how is that boundary determined by sensing, communication, physical geometry and agent availability, and can local information driven reconfiguration shift the boundary.

2. What phenomenon are you actually trying to discover. DECIDED. Whether there is a reproducible operating boundary, driven jointly by sensing, communication, geometry and agent availability, that separates stable from unstable decentralised collective estimation, and whether local reconfiguration can move that boundary.

3. What is the shortest scientifically accurate version of the question. DECIDED. Does a critical information boundary exist in decentralised collective estimation, how does it scale with sensing, communication, geometry and agent availability, and can autonomous information allocation shift it.

4. What is the broader scientific problem. DECIDED. Understanding the information limits of decentralised collective computation, that is, how much local, noisy, communication constrained information a group of autonomous agents needs before their shared estimate of the world becomes unreliable.

5. Why is this problem scientifically important. DECIDED. There is no general account of when collective estimation under decentralised, resource limited conditions remains trustworthy and when it fails, despite this being the normal operating condition for most real autonomous systems.

6. Why does the problem matter specifically for decentralised multi agent systems. DECIDED. Because each agent's local information and local decisions jointly determine a global property, collective estimation stability, and there is no agreed way to predict that global property from local conditions alone.

7. Why does the problem matter specifically for UAV systems. DECIDED. Because UAVs typically have limited onboard sensing and limited communication bandwidth and range, so the boundary is directly relevant to how many UAVs, with what sensors and what communication budget, a task requires to remain reliable.

8. Why does the problem matter in infrastructure free environments. DECIDED. Because there is no GPS, no central server and no guaranteed communication relay, so the swarm must judge, from what is locally available, whether its shared understanding of the world can still be trusted.

9. What existing capability is insufficient. DECIDED. Most existing demonstrations of cooperative estimation assume reasonably good sensing and communication throughout, or study a single constraint in isolation, rather than characterising the joint boundary across constraints.

10. What specific knowledge is currently missing. DECIDED. A reproducible, quantitative account of the joint boundary between stable and unstable decentralised estimation as a function of sensing, communication, geometry and agent availability together, and evidence on whether a decentralised system can shift that boundary using only local information.

11. What observation would constitute a genuinely interesting discovery. DECIDED. A reproducible, non trivial transition in collective estimation performance as information conditions vary, ideally one that a decentralised controller can measurably shift using local information alone.

12. What observation would make the project scientifically uninteresting. DECIDED. Collective estimation performance degrading smoothly and predictably in line with ordinary estimation theory, with no reproducible transition and no scope for a local controller to change the outcome.

13. What observation would directly contradict your central idea. DECIDED. Performance changing gradually with no repeatable transition, or any apparent transition disappearing once connectivity, sensing quality and estimator choice are properly controlled, or a decentralised controller with only local information proving unable to detect or influence the transition at all.

Part II, scope

14. What exactly is AeroNet investigating. DECIDED. Decentralised collective estimation under constrained information, specifically whether a critical information boundary exists and whether local, information driven reconfiguration can shift it.

15. What is explicitly outside the scope. DECIDED. Building a general purpose autonomous UAV platform, developing a new low level flight controller, building a complete search and rescue product, and treating the project as fundamentally an RF engineering exercise.

16. Is AeroNet fundamentally a UAV project, a swarm robotics project, a distributed estimation project, an information theory project, a control project, a multi agent systems project, or a combination. DECIDED. A combination, primarily a distributed estimation and information theory project, using swarm robotics and control as the experimental vehicle and UAVs as the physical substrate.

17. Which field contains the primary scientific contribution. DECIDED. Distributed estimation and information theory, specifically the characterisation of an information boundary in collective estimation.

18. Which fields are merely enabling technologies. DECIDED. Multi agent systems theory, control theory, sensing, communication engineering and UAV hardware.

19. Is the UAV platform the scientific contribution or the experimental substrate. DECIDED. The experimental substrate.

20. Is RF sensing the scientific contribution or merely one test modality. DECIDED. One test modality, chosen for H8.

21. Is the swarm itself the scientific contribution or the system used to test the hypothesis. DECIDED. The system used to test the hypothesis.

22. What claims will AeroNet deliberately not make. DECIDED. That it has built a general purpose swarm product, that the effect is RF specific unless the evidence shows this, that a phase transition exists unless the data supports that specific term, and any novelty claim for ideas the literature review shows are already established.

Part III, operational definitions

23. What exactly does decentralised mean. DECIDED. No agent has access to the complete state of the swarm or the environment, there is no central computer collecting all data or issuing commands, and every decision uses only information available locally to that agent, through its own sensors and through direct communication with neighbours.

24. What information is each agent allowed to access. DECIDED. Its own sensor measurements, its own internal state and history, and whatever a neighbour explicitly communicates to it within the communication model's bandwidth and range limits.

25. What information is each agent forbidden from accessing. DECIDED. The true global state of the swarm, the true state of the target or environment, any other agent's raw sensor data beyond what is communicated, and any information that would only be available to a central coordinator.

26. Is there a central server. DECIDED. No.

27. Is there a leader. DECIDED. No.

28. Is there a global clock. PILOT REQUIRED. The simulator may assume a global clock for reproducibility purposes, while the algorithm itself must not rely on perfect synchronisation; the exact simulator timing model is to be fixed when simulation/communication is built.

29. Is global position available. DECIDED. No, not to any agent, in the research condition.

30. Is GPS available. DECIDED. No, not as an input to the algorithm; GPS may be used only as an independent ground truth reference for physical validation.

31. Is an external map available. DECIDED. No.

32. Is global knowledge of other agents available. DECIDED. No, beyond what is directly sensed or communicated.

33. Is global knowledge of the target or environment available. DECIDED. No, beyond what is directly sensed or communicated.

34. What exactly constitutes collective estimation. DECIDED. The swarm, acting only through local computation and local communication, produces at each agent an estimate of some shared quantity of interest, without any single agent ever holding a complete, centrally fused picture.

35. What exactly is being estimated. LITERATURE REQUIRED. The exact quantity is fixed in variables.md and theory/mathematical_framework.md once the target scenario is chosen.

36. Is the estimated state target position, target state, environmental field, swarm state, relative geometry, or some combination. UNKNOWN. To be decided in theory/mathematical_framework.md after the literature review.

37. What exactly is information. LITERATURE REQUIRED. Defined formally in theory/information_boundary.md.

38. Is information measured using entropy, mutual information, Fisher information, covariance, the Cramer Rao lower bound, innovation, observability, task specific error, or another metric. LITERATURE REQUIRED. Candidates only at this stage, final choice justified in theory/information_boundary.md.

39. Why is that metric appropriate. LITERATURE REQUIRED. To be justified once a metric is chosen, on grounds of local computability, theoretical connection to estimation quality, and comparability across swarm sizes and modalities.

40. What exactly is information availability. DECIDED. The amount of usable, locally accessible information, from sensing and communication combined, that an agent or the collective holds at a given time, under the chosen metric.

41. What exactly is information acquisition. DECIDED. An increase in that available information, through a new measurement, a received message, or a geometric change that improves future observability.

42. What exactly is information loss. DECIDED. A decrease in that available information, through sensor degradation, communication failure, agent loss, or a geometric configuration that reduces observability.

43. What exactly is information allocation. DECIDED. The local decision an agent makes about how to divide its limited sensing, communication and movement resources to acquire or preserve information.

44. What exactly is reconfiguration. DECIDED. A deliberate change in the swarm's physical geometry, undertaken specifically to change future information availability.

45. What exactly is adaptive. DECIDED. A sensing, communication or movement policy that changes in response to locally assessed information conditions, rather than following a fixed schedule.

46. What exactly is stable estimation. LITERATURE REQUIRED, PILOT REQUIRED. Bounded estimation error and bounded uncertainty over a defined observation window, exact bound to be set with reference to the literature and confirmed by pilot experiments.

47. What exactly is unstable estimation. LITERATURE REQUIRED, PILOT REQUIRED. Estimation error or uncertainty that grows without bound, or exceeds the stability threshold for longer than a defined recovery window.

48. What exactly is an information boundary. DECIDED. The set of information conditions at which collective estimation transitions from stable to unstable.

49. What observation would justify calling the boundary critical. EXPERIMENT REQUIRED. A narrow region of information conditions over which the probability of stable estimation falls sharply, demonstrated by repeated controlled trials, not assumed.

50. What observation would mean it is merely a smooth performance curve. EXPERIMENT REQUIRED. A gradual change in the probability of stable estimation across a wide region, with no narrow transition.

51. Under what conditions, if any, would you use the term phase transition. EXPERIMENT REQUIRED. Only if the transition shows the specific statistical signatures associated with that term in the literature, to be defined precisely once the literature review is complete, and only if the data are tested against those signatures rather than the term being used loosely.

52. What exactly does movement becomes computation mean mathematically. LITERATURE REQUIRED. That a change in the geometry variable alters the observation model and therefore the achievable information rate for future measurements, so that a movement action can be shown formally to change the information state, not only the position state; developed in theory/information_boundary.md.

Part IV, system model

53. What is the state of one agent. LITERATURE REQUIRED. To be fixed in theory/mathematical_framework.md, expected to include at minimum position, velocity, heading, local estimate and local uncertainty.

54. What is the state of the whole swarm. DECIDED at the framework level. The joint collection of all individual agent states, never available to any single agent, used in the simulator only for evaluation.

55. What is the environmental state. UNKNOWN. Depends on the chosen estimation target, see question 36.

56. What is the target or source state. UNKNOWN. Depends on the chosen estimation target, see question 36.

57. What are the system dynamics. UNKNOWN. To be fixed in simulation/dynamics, starting from an idealised model and adding realism progressively.

58. Are the dynamics continuous or discrete. UNKNOWN. Likely continuous dynamics integrated at a discrete simulation timestep, to be confirmed when simulation/dynamics is built.

59. What is the timestep. UNKNOWN. To be fixed once the dynamics and sensor update rates are chosen, and validated in simulation/validation.

60. Is time synchronised. PILOT REQUIRED. As for question 28.

61. Are agents homogeneous. UNKNOWN. Default assumption is homogeneous agents for the main phenomenon test, with heterogeneity introduced later as an adversarial condition, to be confirmed in experimental_protocol.md.

62. If not, how do they differ. NOT APPLICABLE at this stage, pending question 61.

63. What does each agent know about itself. DECIDED. Its own state, its own sensor readings, and its own history.

64. What does each agent know about neighbouring agents. DECIDED. Only what neighbours explicitly communicate, within the communication model's limits.

65. What does each agent know about the environment. DECIDED. Only what its own sensors measure, plus anything communicated by neighbours.

66. What does each agent know about the target. DECIDED. Only what its own sensors measure, plus anything communicated by neighbours.

67. What does each agent receive from communication. UNKNOWN. To be fixed in theory/communication_model.md, expected to include neighbour state estimates and possibly raw or partially processed measurements.

68. What does each agent measure directly. UNKNOWN. Depends on the chosen sensing modality, see Part XX.

69. What does each agent infer. DECIDED. Its own local estimate of the shared quantity of interest, and its own assessment of local information conditions.

70. What does each agent control. DECIDED. Its own movement, its own sensing decisions, and its own communication decisions.

71. What is the action space. UNKNOWN. To be fixed in algorithms/controllers, expected to include movement, sensing and communication choices.

72. Are actions continuous or discrete. UNKNOWN. To be decided alongside the action space definition.

73. What are the available high level actions. DECIDED, provisional. Sense, communicate, move and wait.

74. Are there additional actions. UNKNOWN. Possibly a reconfiguration action distinct from ordinary movement, to be confirmed once algorithms/aeronet is designed.

75. What are the resource constraints. DECIDED, provisional. Computational, communication, sensing, movement and energy constraints, each defined individually below.

76. What is the computational constraint. UNKNOWN. Depends on the companion computer chosen in hardware/companion_computer.

77. What is the communication constraint. UNKNOWN. To be fixed in theory/communication_model.md and simulation/communication.

78. What is the sensing constraint. UNKNOWN. To be fixed in theory/sensing_model.md and simulation/sensing.

79. What is the movement constraint. UNKNOWN. To be fixed once the airframe and dynamics model are chosen.

80. What is the energy or resource constraint. UNKNOWN. To be fixed once hardware/power is documented, and represented in simulation as an energy proxy per variables.md.

Part V, research hypotheses, general template

81 to 93. What is the hypothesis, the null hypothesis, the rationale, the independent and dependent variables, the controlled variables, the predicted relationship, the supporting and contradicting quantitative results, the experiment and analysis that test it, the alternative explanation, and how that alternative is tested. DECIDED as a template, answered individually for H1 through H8 in hypotheses.md, and for the sixteen named alternative explanations in falsification_tests.md. This section of the questionnaire is intentionally a template rather than a single answer, and is not repeated again here question by question, since hypotheses.md already gives the complete, filled version for every hypothesis.

Part VI, H1

94. Does a reproducible boundary exist between stable and unstable collective estimation. EXPERIMENT REQUIRED. This is the question H1 exists to answer, and is not assumed in advance.

95. What exactly constitutes stable. See question 46.

96. What exactly constitutes unstable. See question 47.

97. What metric determines the distinction. LITERATURE REQUIRED. Fixed once the primary information and error metrics are chosen, see Part XVIII.

98. Is the boundary expected to be sharp or gradual. EXPERIMENT REQUIRED. No expectation is assumed in either direction, this is precisely what the phenomenon test is designed to determine.

99. How would you statistically distinguish the two. LITERATURE REQUIRED. To be fixed in analysis/boundary_estimation, expected to involve fitting both a sharp transition model and a smooth model to the data and comparing fit quality.

100. How many independent repetitions are required. PILOT REQUIRED. To be set by a power analysis once pilot variance estimates are available, recorded in experimental_protocol.md.

101. What would falsify H1. DECIDED. See falsifying observation for H1 in hypotheses.md.

Part VII, H2

102. Does the boundary depend jointly on sensing. EXPERIMENT REQUIRED.

103. Does it depend on communication. EXPERIMENT REQUIRED.

104. Does it depend on geometry. EXPERIMENT REQUIRED.

105. Does it depend on agent availability. EXPERIMENT REQUIRED.

106. Are these effects additive or interactive. EXPERIMENT REQUIRED. This is the specific question H2 is designed to answer.

107. Are interaction terms required. EXPERIMENT REQUIRED. Determined by the regression analysis in analysis/statistics.

108. What experiment separates these effects. DECIDED. A factorial sweep across the four principal factors, as set out in experimental_protocol.md.

109. What would falsify the claim that they jointly determine the boundary. DECIDED. See falsifying observation for H2 in hypotheses.md.

Part VIII, H3

110. Does reduced information availability increase estimation instability. EXPERIMENT REQUIRED.

111. Which information source is reduced. DECIDED. Each of sensor noise, sensor availability, sensor update rate, communication rate, packet loss, latency, topology, geometry and agent availability, in turn.

112. How is it reduced. UNKNOWN. Exact parameterisation to be fixed per source in simulation/sensing and simulation/communication.

113. Is the reduction gradual. DECIDED. Yes, information sources are swept gradually across a predefined range of levels rather than switched abruptly, so the shape of any transition can be observed.

114. Is the resulting effect monotonic. EXPERIMENT REQUIRED. Expected but not assumed, to be checked directly in the data.

115. Could the effect instead be caused by connectivity. DECIDED. Yes, this is explicitly addressed as an alternative explanation and tested in falsification_tests.md.

116. How will that alternative explanation be controlled. DECIDED. By holding connectivity fixed while varying other information sources, and by holding other sources fixed while varying connectivity, as set out in falsification_tests.md.

Part IX, H4

117. Can physical repositioning increase future information availability. EXPERIMENT REQUIRED.

118. What does increase information mean quantitatively. LITERATURE REQUIRED. Defined once the information metric is chosen, see Part XVIII.

119. What movement changes information. EXPERIMENT REQUIRED. To be identified empirically through the geometry variation experiment.

120. How long does the benefit persist. EXPERIMENT REQUIRED.

121. Does movement have a cost. DECIDED. Yes.

122. How is that cost measured. UNKNOWN. To be fixed as a movement cost or energy proxy in variables.md.

123. Is movement actually better than remaining stationary. EXPERIMENT REQUIRED.

124. Under what conditions. EXPERIMENT REQUIRED.

125. What would falsify H4. DECIDED. See falsifying observation for H4 in hypotheses.md.

Part X, H5

126. Can a decentralised controller detect deteriorating information conditions. EXPERIMENT REQUIRED.

127. What information does the controller use. DECIDED. Only locally available information, as defined in question 24.

128. Is that information locally available. DECIDED. Yes, by construction, this is a design requirement rather than an open question.

129. What constitutes deterioration. LITERATURE REQUIRED. Defined once stable and unstable estimation are precisely fixed, see questions 46 and 47.

130. How quickly must it detect deterioration. EXPERIMENT REQUIRED. To be set relative to the timescale over which the swarm can still usefully act, once that timescale is measured.

131. What action does it take. UNKNOWN. To be fixed in algorithms/aeronet, expected to include adjusting sensing, communication or movement.

132. Does it require global information. DECIDED. No, by design.

133. Does it require training. UNKNOWN. To be decided once the controller design in algorithms/aeronet is fixed, see Part XXV.

134. Does it require a central policy. DECIDED. No.

135. What would falsify H5. DECIDED. See falsifying observation for H5 in hypotheses.md.

Part XI, H6

136. Does adaptive information allocation shift the boundary. EXPERIMENT REQUIRED.

137. What is the baseline. UNKNOWN. The best matched static policy from algorithms/baselines, to be chosen once baseline experiments are complete.

138. What does shift mean quantitatively. DECIDED. A statistically significant difference between the boundary estimated under the adaptive policy and the boundary estimated under the best matched static policy, using the same boundary estimation method.

139. Is the boundary shifted towards lower sensing quality. EXPERIMENT REQUIRED.

140. Lower communication capacity. EXPERIMENT REQUIRED.

141. Higher packet loss. EXPERIMENT REQUIRED.

142. Greater agent failure. EXPERIMENT REQUIRED.

143. Worse geometry. EXPERIMENT REQUIRED.

144. How will the boundary shift be measured. DECIDED. By comparing boundary estimates under each policy using the method in analysis/boundary_estimation.

145. Could the controller simply improve performance without shifting the boundary. DECIDED. Yes, this is explicitly treated as a distinct possibility, not conflated with a genuine boundary shift.

146. How will those two possibilities be distinguished. DECIDED. By estimating the full boundary under each policy, rather than comparing average error at a single fixed operating point, as set out in the AeroNet controller documentation and analysis/boundary_estimation.

Part XII, H7

147. How should the boundary scale with swarm size. UNKNOWN. No functional form is assumed in advance, see theory/scaling_model.md.

148. What values of N will be tested. UNKNOWN. Candidate values are two, four, eight and sixteen agents, to be confirmed once computational and physical limits are known.

149. Why those values. DECIDED, provisional. They span roughly an order of magnitude while remaining computationally and physically tractable, subject to revision.

150. Is there a theoretical prediction. LITERATURE REQUIRED. To be developed in theory/scaling_model.md once the literature review is complete.

151. Does increasing N improve information. EXPERIMENT REQUIRED.

152. Does increasing N increase communication burden. DECIDED. Yes, in general, the exact relationship depends on the communication and topology model.

153. At what point could additional agents become harmful. EXPERIMENT REQUIRED.

154. Does topology change the scaling relationship. EXPERIMENT REQUIRED.

155. What would falsify H7. DECIDED. See falsifying observation for H7 in hypotheses.md.

Part XIII, H8

156. Should the phenomenon persist across sensing modalities. EXPERIMENT REQUIRED. This is precisely what H8 tests, no answer is assumed.

157. Which modalities will be tested. UNKNOWN. RF is the first modality, a second modality is to be chosen once the literature review and simulator design are complete.

158. Why those modalities. UNKNOWN. To be justified once chosen.

159. What properties must remain equivalent between modalities. LITERATURE REQUIRED. To be fixed once the information metric is chosen, expected to include comparable noise and update rate characteristics.

160. What would demonstrate modality independence. DECIDED. A reproducible boundary of similar qualitative character under both modalities.

161. What would demonstrate that the phenomenon is RF specific. DECIDED. The boundary or the phenomenon itself appearing only under RF and not under the alternative modality.

162. If the effect is modality specific, does that invalidate the broader hypothesis. DECIDED. No, it narrows the claim rather than invalidating the project, and must be reported as a genuine, scientifically useful finding rather than hidden or reframed.

Part XIV, alternative explanations

163. Could the observed boundary simply be network disconnection. DECIDED. Possible, tested directly as FT2 in falsification_tests.md.

164. Could it simply be sensor failure. DECIDED. Possible, tested as part of FT3.

165. Could it simply be estimator divergence unrelated to information conditions. DECIDED. Possible, tested as FT4 and FT11.

166. Could it simply be insufficient computational resources. UNKNOWN. Not currently a leading candidate, but to be checked once the companion computer and simulator computational budget are fixed.

167. Could it simply be excessive latency. DECIDED. Possible, tested as FT12.

168. Could it simply be poor geometry. DECIDED. Possible, tested as part of FT2 and FT8.

169. Could it simply be insufficient agent density. DECIDED. Possible, related to FT6 and FT7.

170. Could it simply be a finite size effect. DECIDED. Possible, tested as FT5, FT6 and FT7.

171. Could it be an artefact of the simulator. DECIDED. Possible, tested as FT10, and addressed structurally through simulation/validation.

172. Could it be caused by numerical instability. DECIDED. Possible, tested as FT11.

173. Could it be caused by the chosen information metric. LITERATURE REQUIRED. Addressed by justifying the metric in theory/information_boundary.md and, where feasible, cross checking with a second metric.

174. Could it be caused by the chosen estimator. DECIDED. Possible, tested as FT4, by repeating the phenomenon test with an alternative valid estimator.

175. Could it be caused by the chosen controller. DECIDED. Applies mainly to H6, tested as FT15 and FT16, using the strongest available baseline.

176. Could it be caused by the chosen environment. UNKNOWN. To be checked once the environment model in simulation/environment is fixed, by testing at least one alternative environment configuration.

177. What experiment isolates each alternative. DECIDED. Set out individually for each alternative in falsification_tests.md.

Part XV, literature questions

178 to 196. What has already been demonstrated, what mathematical framework existing work uses, what sensing modality and how many agents it uses, whether it is decentralised, whether it uses communication or physical repositioning, whether it optimises information, whether it estimates a collective state, whether it investigates a critical boundary, whether it experimentally validates the result, what limitation remains, whether AeroNet is actually different and exactly how, which paper is closest to AeroNet, which paper most threatens the novelty claim, what terminology the existing literature uses for the proposed phenomenon, whether AeroNet is using a new name for an existing concept, and if so what is genuinely new. LITERATURE REQUIRED for all of these questions, in full. These are answered per paper in literature_review.md, using the paper record template given there, and are not answered in the abstract here since doing so without the literature review would risk exactly the kind of unjustified novelty claim this document is meant to prevent. The novelty_matrix.md file is populated directly from these answers once the literature review is complete.

Part XVI, novelty

197. What is the smallest defensible novelty claim. DECIDED, provisional. A measurable, reproducible critical boundary governing collective estimation under multiple jointly varying information constraints, characterised empirically.

198. What is the strongest defensible novelty claim. DECIDED, provisional, pending literature review. A generalised, dimensionless information quantity that predicts the transition across different swarm sizes, environments and sensing modalities, together with evidence that a decentralised controller can shift the measured boundary rather than merely improve average case performance.

199. What evidence supports the distinction. LITERATURE REQUIRED. To be filled in novelty_matrix.md once literature_review.md is complete.

200. What prior work overlaps directly. LITERATURE REQUIRED.

201. What prior work overlaps partially. LITERATURE REQUIRED.

202. What does AeroNet combine that existing work does not. DECIDED, provisional. The joint treatment of sensing, communication, geometry and agent availability as a single information condition governing a measurable boundary, together with a decentralised controller tested for its ability to shift that boundary rather than only to improve performance at a fixed point.

203. Is that combination itself scientifically meaningful. LITERATURE REQUIRED. To be judged once the literature review is complete, not assumed.

204. Is there a new mathematical object. UNKNOWN. Depends on whether the candidate boundary function in theory/information_boundary.md survives contact with the literature and the data.

205. Is there a new empirical phenomenon. EXPERIMENT REQUIRED. Depends on whether H1 is supported.

206. Is there a new controller. UNKNOWN. Depends on the literature review of adaptive and information driven controllers.

207. Is there a new experimental methodology. UNKNOWN. Possibly, in the specific combination of boundary estimation and ablation used here, to be judged after the literature review.

208. Is there a new scaling law. EXPERIMENT REQUIRED. Depends on H7.

209. Is there a new physical validation. UNKNOWN. Depends on whether comparable physical validation already exists in the literature for this specific combination of constraints.

210. Which of these is actually the contribution. UNKNOWN. To be settled once the literature review, theory and experiments are complete, and stated plainly, without inflation, in the final paper.

Part XVII, mathematical model

211. What is the state vector. UNKNOWN. To be fixed in theory/mathematical_framework.md.

212. What is the observation equation. UNKNOWN. To be fixed in theory/sensing_model.md, once the sensing modality is chosen.

213. What is the process equation. UNKNOWN. To be fixed in theory/mathematical_framework.md, once the dynamics model is chosen.

214. What is the measurement noise model. UNKNOWN. To be fixed in theory/sensing_model.md.

215. What is the communication graph. UNKNOWN. To be fixed in theory/communication_model.md.

216. Is the graph directed or undirected. UNKNOWN. Likely undirected for symmetric communication links, to be confirmed.

217. Is it static or dynamic. DECIDED. Dynamic, since agents move and links can be created or lost.

218. How are edges created. UNKNOWN. Likely a range and line of sight based rule, to be fixed in theory/communication_model.md.

219. How are edges lost. UNKNOWN. Likely range, obstruction, packet loss or agent failure, to be fixed in theory/communication_model.md.

220. What is the communication model. UNKNOWN. To be fixed in theory/communication_model.md.

221. What is the estimator. UNKNOWN. To be fixed in theory/estimator_model.md.

222. What is the uncertainty representation. UNKNOWN. To be fixed in theory/estimator_model.md, likely a covariance based representation.

223. What is the control policy. UNKNOWN. To be fixed in algorithms/controllers and algorithms/aeronet.

224. What is the objective function. UNKNOWN. Candidate objectives are given in Part XXV.

225. What are the constraints. DECIDED at a high level. Computational, communication, sensing, movement and energy constraints, as in questions 76 to 79.

226. What constitutes convergence. LITERATURE REQUIRED. To be tied to the stable estimation definition once fixed.

227. What constitutes divergence. LITERATURE REQUIRED. To be tied to the unstable estimation definition once fixed.

228. What constitutes bounded uncertainty. LITERATURE REQUIRED. To be defined numerically alongside stable estimation.

229. What constitutes unbounded uncertainty. LITERATURE REQUIRED. To be defined numerically alongside unstable estimation.

230. What candidate quantity represents information. LITERATURE REQUIRED. See Part XVIII.

231. What candidate quantity represents information loss. LITERATURE REQUIRED. The negative change in whichever information quantity is chosen.

232. Can the boundary be expressed mathematically. UNKNOWN. The candidate form is given in research_question.md and theory/information_boundary.md, but is not assumed correct.

233. Can it be normalised. UNKNOWN. This is one of the central questions of theory/scaling_model.md.

234. Can it be dimensionless. UNKNOWN. As above.

235. Can it be compared across swarm sizes. EXPERIMENT REQUIRED. This is H7.

236. Can it be compared across sensing modalities. EXPERIMENT REQUIRED. This is H8.

Part XVIII, information metric

237. What is your primary information metric. LITERATURE REQUIRED. Not yet chosen, see theory/information_boundary.md.

238. Why. LITERATURE REQUIRED. To be justified once chosen.

239. What alternatives were considered. LITERATURE REQUIRED. The full candidate list is entropy, mutual information, Fisher information, covariance, the Cramer Rao lower bound, innovation, observability and task specific error.

240. Why were those alternatives rejected. LITERATURE REQUIRED. To be documented in theory/information_boundary.md once a choice is made, including honestly recording any candidate that was rejected only for practical reasons such as computability.

241. Is the metric computable locally. LITERATURE REQUIRED. A required property, to be checked for whichever metric is chosen.

242. Is it computable centrally only. LITERATURE REQUIRED. If so, that metric is disqualified for use inside the controller and may only be used for evaluation in the simulator.

243. Can it be estimated in real time. LITERATURE REQUIRED. A required property for use inside the controller.

244. Does it require knowledge unavailable to the swarm. LITERATURE REQUIRED. If so, that metric is disqualified for use inside the controller, per question 242.

245. Is it theoretically related to estimation quality. LITERATURE REQUIRED. A required property.

246. Is it experimentally measurable. LITERATURE REQUIRED. A required property.

247. Is it robust to sensor bias. LITERATURE REQUIRED. To be checked once chosen.

248. Is it robust to packet loss. LITERATURE REQUIRED. To be checked once chosen.

249. Is it robust to changing geometry. LITERATURE REQUIRED. To be checked once chosen.

250. Is it comparable across different N. EXPERIMENT REQUIRED. Related to H7 and theory/scaling_model.md.

251. What are its known limitations. LITERATURE REQUIRED. To be documented in theory/information_boundary.md once the metric is chosen.

Part XIX, estimator

252. What estimator will be used. LITERATURE REQUIRED. To be fixed in theory/estimator_model.md and algorithms/estimators.

253. Why. LITERATURE REQUIRED. To be justified once chosen.

254. What assumptions does it make. LITERATURE REQUIRED. To be documented once chosen.

255. Does every agent run the same estimator. DECIDED, provisional. Yes, for the main phenomenon test, to keep the estimator held constant while information conditions are varied; a different estimator is used only as an explicit alternative in FT4.

256. How are measurements fused. UNKNOWN. To be fixed in theory/estimator_model.md.

257. How are stale measurements handled. UNKNOWN. To be fixed in theory/estimator_model.md, likely through explicit message age weighting.

258. How are missing measurements handled. UNKNOWN. To be fixed in theory/estimator_model.md.

259. How are failed agents handled. UNKNOWN. To be fixed in theory/estimator_model.md and tested in Part XXIII.

260. How is uncertainty propagated. UNKNOWN. To be fixed once the estimator is chosen.

261. How is estimator stability measured. LITERATURE REQUIRED. Tied to the stable and unstable estimation definitions once fixed.

262. What estimator baselines will be included. UNKNOWN. To be fixed once algorithms/baselines is populated following the literature review.

263. Is there a centralised oracle. DECIDED. Yes, as a baseline only, never as part of the decentralised system under test.

264. What information does the oracle receive. DECIDED. The full, true global state of the swarm and environment, used only to establish an upper bound on achievable performance for comparison.

Part XX, sensing

265. What is the first sensing modality. DECIDED, provisional. RF, consistent with H8 and the role of RF described in research_question.md.

266. Why. DECIDED. RF is a demanding and realistic constraint on a UAV swarm and is already a stated experimental substrate for the project, though it is treated as one modality rather than the subject of the research.

267. What does the sensor measure. LITERATURE REQUIRED. To be fixed in theory/sensing_model.md once the exact RF sensing approach, such as received signal strength or bearing, is chosen.

268. What is its noise model. UNKNOWN. To be fixed in theory/sensing_model.md.

269. What is its bias model. UNKNOWN. To be fixed in theory/sensing_model.md.

270. What is its update rate. UNKNOWN. To be fixed in theory/sensing_model.md and validated against real hardware once chosen.

271. What is its range. UNKNOWN. To be fixed once the sensor is chosen.

272. What is its detection probability. UNKNOWN. To be fixed once the sensor is chosen.

273. What happens when the signal is absent. UNKNOWN. To be fixed in simulation/sensing, likely modelled as a missing observation.

274. What happens when the signal is weak. UNKNOWN. To be fixed in simulation/sensing, likely modelled as increased noise or reduced detection probability.

275. What happens when the signal is ambiguous. UNKNOWN. To be fixed once the sensing modality and estimator are chosen.

276. What happens when measurements are corrupted. UNKNOWN. To be fixed in simulation/sensing, likely modelled through the bias and outlier components of the noise model.

277. What sensing parameters will be swept. DECIDED, provisional. Noise level, update rate and availability, with exact levels fixed in experimental_protocol.md.

Part XXI, communication

278. What communication architecture is simulated. UNKNOWN. To be fixed in theory/communication_model.md, likely a range limited, possibly multi hop, wireless model.

279. What information can agents exchange. UNKNOWN. To be fixed once the estimator's fusion approach is chosen, likely local state estimates and their uncertainty.

280. How large are messages. UNKNOWN. To be fixed once the message content is decided.

281. How often are messages sent. UNKNOWN. To be fixed in theory/communication_model.md, and swept as an experimental variable.

282. What is the bandwidth. UNKNOWN. To be fixed once real hardware is chosen, and modelled explicitly as a constraint in simulation/communication.

283. What is the latency. UNKNOWN. To be swept as an experimental variable, with realistic values informed by the hardware chosen in hardware/communications.

284. What is packet loss. UNKNOWN. To be swept as an experimental variable.

285. Is packet loss independent or correlated. UNKNOWN. To be fixed in simulation/communication, with an independent model as the default and a correlated model as an adversarial condition.

286. Can the topology fragment. DECIDED. Yes, this is required to test agent failure and adversarial conditions.

287. Can agents reconnect. DECIDED. Yes.

288. Are messages ordered. UNKNOWN. To be fixed in simulation/communication.

289. Can messages arrive late. DECIDED. Yes, this is how latency is represented.

290. Can messages be duplicated. UNKNOWN. To be fixed in simulation/communication, default assumption is no duplication unless a specific adversarial test requires it.

291. What communication conditions will be tested. DECIDED, provisional. Bandwidth, message frequency, latency, packet loss and topology, with exact levels fixed in experimental_protocol.md.

Part XXII, geometry

292. What geometric variables matter. UNKNOWN. To be fixed in theory/geometry_model.md, expected to include inter agent spacing, relative bearing and overall formation shape.

293. What is the initial configuration. UNKNOWN. To be fixed in simulation/scenarios.

294. What formations are tested. UNKNOWN. To be fixed once theory/geometry_model.md is complete.

295. What constitutes good geometry. LITERATURE REQUIRED. To be defined in terms of observability once the estimator and sensing model are fixed.

296. What constitutes poor geometry. LITERATURE REQUIRED. As above.

297. How does geometry affect sensing. LITERATURE REQUIRED. To be fixed in theory/geometry_model.md and theory/sensing_model.md together.

298. How does geometry affect communication. LITERATURE REQUIRED. To be fixed in theory/geometry_model.md and theory/communication_model.md together.

299. How does geometry affect observability. LITERATURE REQUIRED. To be fixed in theory/geometry_model.md, drawing on the observability literature identified in literature_review.md.

300. Can agents intentionally reposition. DECIDED. Yes, this is required for H4, H5 and H6.

301. What is the cost of repositioning. UNKNOWN. To be fixed as a movement cost or energy proxy in variables.md.

302. What is the timescale of geometric adaptation. UNKNOWN. To be fixed once the dynamics and controller are chosen.

Part XXIII, agent failure

303. What constitutes agent failure. UNKNOWN. To be fixed in theory/estimator_model.md and simulation/scenarios, likely covering loss of sensing, loss of communication, or complete loss of the agent.

304. Is failure permanent or temporary. DECIDED, provisional. Both are tested, permanent failure for the main failure sweep and temporary failure as a recovery time test.

305. What fraction of agents can fail. UNKNOWN. To be fixed in experimental_protocol.md.

306. Are failures random. DECIDED, provisional. Yes, for the main failure sweep, with spatially correlated failure tested separately as an adversarial condition.

307. Are failures spatially correlated. DECIDED. Tested as a distinct adversarial condition, not the default assumption.

308. Can neighbouring agents detect failure. UNKNOWN. To be fixed once the communication model defines how the absence of expected messages is handled.

309. How does the estimator react. UNKNOWN. To be fixed in theory/estimator_model.md.

310. How does the controller react. UNKNOWN. To be fixed in algorithms/aeronet.

311. Does the boundary deform predictably. EXPERIMENT REQUIRED. Related to H2 and FT8.

312. What would falsify the failure hypothesis. DECIDED. See falsifying observation for H2 and H3 in hypotheses.md, and FT2 in falsification_tests.md, which cover failure induced connectivity loss specifically.

Part XXIV, baselines

313 to 323. What algorithm is compared, why it is relevant, what information it receives against what AeroNet receives, whether computational resources, sensing, communication and movement constraints are equivalent, whether the comparison is fair, what metric is used, and what constitutes a meaningful difference. LITERATURE REQUIRED for the specific baseline set, to be finalised once literature_review.md is complete, from the candidate list already given in research_question.md, namely random movement, Levy style exploration where appropriate, potential field control, fixed formation, periodic communication, event triggered communication, information gain control, communication aware movement, consensus based estimation, a centralised oracle, no communication, no repositioning, adaptive sensing only, adaptive communication only, and adaptive motion only. The fairness rule is DECIDED and non negotiable: AeroNet must not receive information that its comparison systems do not receive, and every baseline is given equivalent computational, sensing, communication and movement resources unless the comparison is explicitly designed to test the effect of removing one of those resources, such as the no communication baseline. The metric used for comparison is the same primary and secondary metrics used throughout, fixed in variables.md, and a meaningful difference is defined statistically in analysis/statistics, not by inspection.

Part XXV, AeroNet controller

324. What exactly does AeroNet decide. DECIDED. Sensing, communication, movement, or waiting, using only local information.

325. Does it choose sensing. DECIDED. Yes.

326. Does it choose communication. DECIDED. Yes.

327. Does it choose movement. DECIDED. Yes.

328. Does it choose waiting. DECIDED. Yes, waiting is included as an explicit action.

329. Does it choose all four. DECIDED. Yes.

330. What information does it use. DECIDED. Only locally available information, as defined in question 24.

331. What information is explicitly unavailable. DECIDED. The true global state of the swarm and environment, and any other agent's raw data beyond what is communicated, as in question 25.

332. What objective does it optimise. UNKNOWN. Candidates are given in the next three questions, final choice to be fixed in algorithms/aeronet once the information metric is chosen.

333. Does it maximise information. UNKNOWN. A candidate objective.

334. Does it minimise uncertainty. UNKNOWN. A candidate objective, closely related to maximising information depending on the metric chosen.

335. Does it optimise information per resource cost. UNKNOWN. A candidate objective, considered the most principled option pending the literature review, since it directly represents the resource constrained nature of the problem.

336. Does it use prediction. UNKNOWN. To be decided in algorithms/aeronet.

337. Does it use learning. UNKNOWN. To be decided in algorithms/aeronet, after the literature review has established whether a learned or a hand designed policy is more appropriate for a first, interpretable version of the controller.

338. Does it use reinforcement learning. UNKNOWN. Only if question 337 favours a learned policy, and even then not assumed as the default choice.

339. Does it require training data. UNKNOWN. Depends on questions 337 and 338.

340. Is the policy deterministic. UNKNOWN. To be fixed in algorithms/aeronet.

341. Is it stochastic. UNKNOWN. As above.

342. Can it operate without a central coordinator. DECIDED. Yes, this is a design requirement, not an open question.

343. What happens if communication disappears. UNKNOWN. To be fixed in algorithms/aeronet and tested directly under FT2 and the adversarial communication conditions in Part XXXII.

344. What happens if sensors fail. UNKNOWN. To be fixed in algorithms/aeronet and tested under the sensor dropout adversarial condition.

345. What happens if an agent disappears. UNKNOWN. To be fixed in algorithms/aeronet and tested under Part XXIII.

Part XXVI, simulator

346. What simulator will be used. UNKNOWN. To be chosen once the required physics, question 348, are fixed, weighing an existing robotics simulator against a purpose built lightweight simulator suited to large parameter sweeps.

347. Why. UNKNOWN. To be justified once chosen.

348. What physics are necessary. UNKNOWN. To be fixed in simulation/dynamics, likely simplified rigid body flight dynamics rather than full aerodynamic simulation, since the scientific question concerns information, not flight mechanics.

349. What physics are unnecessary. DECIDED, provisional. Detailed aerodynamic and structural simulation, since these are not the subject of the research question.

350. What is simplified. UNKNOWN. To be documented explicitly in simulation/dynamics and simulation/README.md as assumptions are made.

351. What is realistic. UNKNOWN. As above, expected to include sensor noise, communication constraints and estimator behaviour, which are central to the research question.

352. Which assumptions could affect the conclusion. UNKNOWN. To be reviewed explicitly once the simulator is built, and tested directly through simulation/validation and FT10.

353. How will the simulator be validated. DECIDED. Through the checks listed in simulation/validation, covering the sensor model, communication model, dynamics, estimator, ground truth, random seed reproducibility and boundary conditions.

354. What analytical cases can it reproduce. UNKNOWN. To be identified once the estimator is chosen, likely simple cases with a known closed form solution, such as a single static agent with linear Gaussian measurements.

355. Can identical seeds reproduce identical results. DECIDED. This is a requirement, to be confirmed in simulation/validation before any experiment is trusted.

356. Can independent implementations reproduce the result. UNKNOWN. Desirable but not guaranteed within the scope of a single project, to be revisited if collaboration, see Part XLIII, makes this possible.

357. What simulator limitations must be reported. UNKNOWN. To be documented honestly in the relevant paper's limitations section once known.

Part XXVII, experimental design

358. What is the experimental unit. UNKNOWN. To be fixed in experimental_protocol.md, expected to be one complete simulated run of the swarm under one set of information conditions and one random seed.

359. What is one trial. DECIDED. One run of the experimental unit above.

360. What is one condition. DECIDED. One specific combination of levels of the independent variables.

361. What is one independent replicate. DECIDED. One trial run with a distinct random seed under the same condition.

362. How many replicates. PILOT REQUIRED. To be set by a power analysis once pilot variance estimates are available.

363. Why. DECIDED. So that the number of replicates is justified by the actual variability observed, rather than chosen arbitrarily.

364. What are the independent variables. DECIDED, provisional. Swarm size, sensing uncertainty, sensing rate, communication rate, packet loss, latency, network topology, agent failure and geometry, as listed in experimental_protocol.md.

365. What are their levels. UNKNOWN. To be fixed in experimental_protocol.md before the main campaign, and not chosen after seeing results.

366. What are the dependent variables. UNKNOWN. The primary endpoint, once chosen, plus the secondary endpoints listed in variables.md.

367. What are the controls. UNKNOWN. Whatever variables are not being swept in a given experiment, held fixed and documented explicitly.

368. What is randomised. DECIDED. The random seed governing noise realisations, scenario generation, and any stochastic policy.

369. What is held constant. UNKNOWN. To be documented per experiment in its configuration file.

370. What is the primary endpoint. UNKNOWN. To be chosen from the candidate metrics in Part XVIII and Part XXVIII once the information metric is fixed.

371. What are secondary endpoints. UNKNOWN. Listed as candidates in variables.md.

372. What is the analysis population. DECIDED. All trials that meet the pre registered inclusion criteria in experimental_protocol.md, before any exclusions are applied.

373. What data can be excluded. UNKNOWN. To be fixed in experimental_protocol.md before the main campaign, expected to cover clearly identifiable simulator or logging faults rather than inconvenient results.

374. Who decides exclusions. DECIDED. Exclusion criteria are fixed in writing before the main campaign runs, so no individual judgement call is required afterwards; any post hoc exclusion not covered by the pre registered criteria is reported openly rather than applied silently.

375. Are exclusions decided before seeing results. DECIDED. Yes, this is a firm rule, consistent with Rule 8 in CONTRIBUTING.md.

Part XXVIII, statistical analysis

376. What statistical model will be used. LITERATURE REQUIRED. To be fixed in analysis/statistics once the primary endpoint and its expected distribution are known.

377. Why is it appropriate. LITERATURE REQUIRED. To be justified once chosen.

378. What assumptions does it make. LITERATURE REQUIRED. To be documented once chosen.

379. How will assumptions be checked. LITERATURE REQUIRED. Through standard diagnostic checks appropriate to the chosen model, documented in analysis/statistics.

380. What confidence level will be used. DECIDED, provisional. Ninety five per cent, subject to revision if the multiple comparison correction in question 384 requires a different working level.

381. What effect size matters scientifically. UNKNOWN. To be fixed once the primary endpoint and its natural units are known.

382. What effect size matters practically. UNKNOWN. As above, and to be informed by the physical validation requirements in Part XXXIII.

383. How will uncertainty be reported. DECIDED. Using confidence intervals or credible intervals throughout, not point estimates alone.

384. How will multiple comparisons be handled. LITERATURE REQUIRED. A correction method, such as a false discovery rate control, to be fixed in analysis/statistics before the main campaign.

385. How will repeated measurements be handled. LITERATURE REQUIRED. Likely through a mixed effects model treating replicate and condition as structured factors, to be confirmed in analysis/statistics.

386. How will random seeds be treated. DECIDED. As the unit of independent replication, not pooled or cherry picked, consistent with Rule 8 in CONTRIBUTING.md.

387. How will missing data be treated. UNKNOWN. To be fixed in analysis/preprocessing, and reported rather than silently dropped.

388. How will outliers be treated. UNKNOWN. To be fixed in analysis/preprocessing, using a pre specified rule rather than a case by case judgement.

389. Will bootstrap methods be used. LITERATURE REQUIRED. Likely yes, for boundary uncertainty estimation in particular, to be confirmed in analysis/boundary_estimation.

390. Will regression be used. DECIDED. Yes, for H2 in particular, to test for interaction effects.

391. Will interaction terms be used. DECIDED. Yes, required to test H2.

392. How will boundary uncertainty be quantified. LITERATURE REQUIRED. To be fixed in analysis/boundary_estimation, likely through bootstrap resampling of the fitted transition location.

Part XXIX, boundary detection

393. What exactly is being plotted. UNKNOWN. To be fixed once the primary endpoint and independent variables are chosen, expected to be a stability measure plotted against one or more information conditions.

394. What is the independent axis. UNKNOWN. One or more of the information conditions in question 364.

395. What is the dependent axis. UNKNOWN. The primary endpoint.

396. What defines the stable region. LITERATURE REQUIRED. See question 46.

397. What defines the unstable region. LITERATURE REQUIRED. See question 47.

398. How is the transition located. LITERATURE REQUIRED. To be fixed in analysis/boundary_estimation, likely by fitting a transition model to the data.

399. How wide is the uncertainty around it. EXPERIMENT REQUIRED. To be measured, not assumed.

400. Is the boundary continuous. EXPERIMENT REQUIRED.

401. Is it discontinuous. EXPERIMENT REQUIRED.

402. Is there hysteresis. EXPERIMENT REQUIRED. Not tested unless the main phenomenon test suggests it is worth investigating, since it is not part of the core hypothesis set.

403. Does the transition depend on initial conditions. EXPERIMENT REQUIRED.

404. Does it depend on swarm size. EXPERIMENT REQUIRED. This is H7.

405. Does it depend on topology. EXPERIMENT REQUIRED. This is part of H2 and H7.

406. Does it depend on sensing modality. EXPERIMENT REQUIRED. This is H8.

407. Does it depend on estimator choice. EXPERIMENT REQUIRED. Tested directly as FT4.

408. What result would prove there is no single boundary. DECIDED. A set of experiments in which no consistent transition location can be identified across replicates, or in which the transition location varies so much with unrelated factors that no single boundary can be meaningfully reported, in which case the finding is reported as such rather than forced into a single boundary claim.

Part XXX, scaling

409. What happens as N increases. EXPERIMENT REQUIRED.

410. What happens as N decreases. EXPERIMENT REQUIRED.

411. Does information increase linearly. EXPERIMENT REQUIRED.

412. Does communication cost increase linearly. UNKNOWN. Depends on the topology model, to be checked once theory/communication_model.md is fixed.

413. Does the boundary scale linearly. EXPERIMENT REQUIRED.

414. Is there a saturation point. EXPERIMENT REQUIRED.

415. Is there an optimal density. EXPERIMENT REQUIRED.

416. Does topology alter scaling. EXPERIMENT REQUIRED.

417. Can a normalised variable collapse results from different N. EXPERIMENT REQUIRED. This is the most ambitious part of H7 and theory/scaling_model.md.

418. What would constitute evidence for universality. DECIDED. Results from different values of N collapsing onto a single curve once plotted against a suitably normalised information variable, within statistical uncertainty.

419. What would falsify universality. DECIDED. Results from different values of N failing to collapse under any normalisation tried, in which case the boundary must be reported as N dependent rather than universal.

Part XXXI, ablation

420. What happens without adaptive sensing. EXPERIMENT REQUIRED.

421. What happens without adaptive communication. EXPERIMENT REQUIRED.

422. What happens without adaptive movement. EXPERIMENT REQUIRED.

423. What happens without information estimation. EXPERIMENT REQUIRED.

424. What happens without geometry adaptation. EXPERIMENT REQUIRED.

425. What happens without failure handling. EXPERIMENT REQUIRED.

426. What happens without prediction. EXPERIMENT REQUIRED, conditional on question 336 confirming that prediction is part of the controller at all.

427. What happens without each major AeroNet component. DECIDED. Tested systematically as the ablation set listed in experiments/ablations/README.md.

428. Which component is expected to contribute most. UNKNOWN. No expectation is assumed in advance, this is exactly what the ablation experiment is designed to reveal.

429. What result would show that a component is unnecessary. DECIDED. Removing that component produces no statistically significant change in the boundary shift measured for H6.

Part XXXII, adversarial testing

430. What happens under severe packet loss. EXPERIMENT REQUIRED.

431. What happens under severe latency. EXPERIMENT REQUIRED.

432. What happens under sensor bias. EXPERIMENT REQUIRED.

433. What happens under sensor dropout. EXPERIMENT REQUIRED.

434. What happens under agent failure. EXPERIMENT REQUIRED.

435. What happens under network fragmentation. EXPERIMENT REQUIRED.

436. What happens under poor geometry. EXPERIMENT REQUIRED.

437. What happens under rapidly changing conditions. EXPERIMENT REQUIRED.

438. What happens under misleading measurements. EXPERIMENT REQUIRED.

439. What happens under heterogeneous agents. EXPERIMENT REQUIRED, conditional on question 61.

440. What happens when several failures occur simultaneously. EXPERIMENT REQUIRED, tested as a combined adversarial condition once the individual conditions above are understood.

Part XXXIII, physical experiment

441. What exactly must be demonstrated physically. UNKNOWN. To be fixed once a specific, quantitative simulation prediction is selected for testing, per experimental_protocol.md.

442. Which simulation prediction will be tested. UNKNOWN. To be chosen once the main simulation campaign has produced a clear, falsifiable prediction, most likely a specific boundary location under a specific, physically reproducible information condition.

443. Why is that prediction physically important. UNKNOWN. To be justified once chosen.

444. What is the minimum physical swarm size. UNKNOWN. To be fixed once resources and safety requirements are known, expected to be small, such as two or three aircraft, given the practical and safety constraints of physical UAV testing.

445. What is the maximum justified physical swarm size. UNKNOWN. To be fixed once resources and safety requirements are known.

446. What independent ground truth system is used. UNKNOWN. To be fixed in hardware/ground_truth, must not rely on the swarm's own estimate.

447. What measurements are collected. UNKNOWN. To be fixed in hardware/test_procedures, expected to include position, communication statistics and estimator output.

448. How are timestamps synchronised. UNKNOWN. To be fixed in hardware/integration.

449. How is communication measured. UNKNOWN. To be fixed in hardware/communications.

450. How is sensor performance measured. UNKNOWN. To be fixed in hardware/sensing.

451. How is estimator performance measured. UNKNOWN. Against the independent ground truth in hardware/ground_truth.

452. How is simulation to hardware discrepancy quantified. UNKNOWN. To be fixed in analysis/hardware_comparison.

453. What discrepancies are acceptable. UNKNOWN. To be fixed once a specific prediction and measurement plan exist, and stated in advance rather than decided after seeing the physical results.

454. What discrepancies would invalidate the model. UNKNOWN. As above.

455. What safety and institutional approvals are required. UNKNOWN. To be fixed in competition/documentation, in consultation with the relevant school, laboratory and aviation authorities.

456. What work must be conducted under appropriate supervision. DECIDED. All physical flight testing, per hardware/mechanical/README.md and competition/documentation/README.md.

Part XXXIV, hardware

457. What flight platform will be used. UNKNOWN. To be fixed in hardware/mechanical once requirements from the physical validation target are known.

458. Why. UNKNOWN. To be justified once chosen.

459. What mature flight control system will be used. UNKNOWN. To be fixed in hardware/flight_controller, chosen from an existing, well established platform rather than developed from scratch, per the hardware philosophy in research_question.md.

460. What companion computer is required. UNKNOWN. To be fixed in hardware/companion_computer once the computational requirements of the estimator and controller are known.

461. What sensors are required. UNKNOWN. To be fixed in hardware/sensing once the sensing modality, question 265, is finalised.

462. What communication hardware is required. UNKNOWN. To be fixed in hardware/communications.

463. What independent ground truth system is required. UNKNOWN. To be fixed in hardware/ground_truth.

464. What data must be logged onboard. UNKNOWN. To be fixed in hardware/integration.

465. What data must be logged externally. UNKNOWN. To be fixed in hardware/ground_truth and hardware/integration.

466. How will hardware versions be controlled. DECIDED. Every hardware revision receives a hardware version identifier, recorded in experiment manifests, per Rule 15 in CONTRIBUTING.md.

467. How will software versions be controlled. DECIDED. Through git commit references recorded in every experiment manifest, per Rule 14 in CONTRIBUTING.md.

468. How will individual aircraft be identified. UNKNOWN. To be fixed in hardware/integration, likely a simple unique identifier per airframe.

469. How will hardware differences between aircraft be measured. UNKNOWN. To be fixed in hardware/test_procedures.

470. What components must be identical. UNKNOWN. To be fixed once the platform is chosen, expected to include the flight controller and companion computer at minimum.

471. What components can vary. UNKNOWN. To be fixed once the platform is chosen.

472. What physical limitations could affect the scientific result. UNKNOWN. To be documented honestly once known, and reported as a limitation in Paper 5 or Paper 1 as appropriate.

Part XXXV, safety and compliance

473. What aviation requirements apply. UNKNOWN. To be identified in competition/documentation, in consultation with the relevant national aviation authority and any school or laboratory policy.

474. What school or laboratory requirements apply. UNKNOWN. To be identified in competition/documentation.

475. What adult or supervisor involvement is required. UNKNOWN. To be identified in competition/documentation, expected to be mandatory for all physical flight testing.

476. What experiments require prior approval. UNKNOWN. To be identified in competition/documentation, expected to include at minimum all outdoor and all physical flight testing.

477. What environments are permitted. UNKNOWN. To be identified in competition/documentation.

478. What environments are prohibited. UNKNOWN. To be identified in competition/documentation.

479. What is the emergency procedure. UNKNOWN. To be written in hardware/test_procedures before any physical flight testing begins.

480. What is the system shutdown procedure. UNKNOWN. To be written in hardware/test_procedures before any physical flight testing begins.

481. What testing can occur safely on a bench. DECIDED, provisional. All sensor, communication and estimator validation not requiring actual flight, per hardware/test_procedures/README.md.

482. What testing requires controlled flight facilities. DECIDED, provisional. All physical validation experiments involving airborne aircraft, per experiments/hardware_validation/README.md.

483. What data or privacy considerations exist. UNKNOWN. To be reviewed once the physical testing environment is known, particularly if testing occurs anywhere members of the public might be recorded.

Part XXXVI, reproducibility

484. Can someone clone the repository and reproduce the simulation. DECIDED. This is a requirement, to be delivered through environment.yml, requirements.txt and the runners in simulation/runners.

485. Can they reproduce the exact configuration. DECIDED. Yes, every experiment has a configuration file in experiments/configs, per Rule 1 and Rule 2 in CONTRIBUTING.md.

486. Can they reproduce the exact random seeds. DECIDED. Yes, seeds are recorded in every experiment manifest, per Rule 3 in CONTRIBUTING.md.

487. Can they reproduce every figure. DECIDED. Yes, every figure is generated by code in analysis/visualisation, per Rule 4 in CONTRIBUTING.md.

488. Can they reproduce every table. DECIDED. Yes, by the same rule.

489. Can they trace every result to raw data. DECIDED. Yes, per Rule 1 in CONTRIBUTING.md.

490. Can they trace every raw dataset to a protocol. DECIDED. Yes, per Rule 2 in CONTRIBUTING.md and the manifest fields in experiments/manifests/README.md.

491. Can they identify the exact code version. DECIDED. Yes, through the git commit field in every manifest.

492. Can they identify the hardware version. DECIDED. Yes, through the hardware version field in every manifest.

493. Can an independent researcher reproduce the main conclusion. UNKNOWN. This is the ultimate test of the reproducibility infrastructure and can only be answered once the main dataset exists and the full pipeline in analysis/reproducibility has been exercised end to end by someone other than the original author.

Part XXXVII, data management

494. What is stored as raw data. DECIDED. Immutable, unmodified experiment output, in experiments/raw, per Rule 12 in CONTRIBUTING.md.

495. What is stored as processed data. DECIDED. Data derived from raw data through a documented step in analysis/preprocessing, stored in experiments/processed, per Rule 12.

496. What is metadata. UNKNOWN. To be fixed in experiments/manifests/README.md, expected to include everything in the manifest fields already listed.

497. What is the file format. UNKNOWN. To be fixed once the simulator is chosen, likely a plain, widely readable format such as CSV or Parquet for tabular data, and YAML for configuration.

498. How are datasets named. UNKNOWN. To be fixed once the experiment identifier scheme, question 499, is chosen.

499. How are experiments identified. DECIDED, provisional. A unique experiment identifier per Rule 13 in CONTRIBUTING.md, exact format to be fixed in experiments/manifests/README.md.

500. How are failed experiments recorded. DECIDED. Retained, not deleted, with their status recorded in the manifest, per Rule 7 in CONTRIBUTING.md.

501. How are corrupted experiments recorded. DECIDED. As above, with the corruption noted explicitly in the manifest status field rather than the data being silently removed.

502. How are data backups maintained. UNKNOWN. To be decided based on available storage and computing resources.

503. How are data integrity checks performed. UNKNOWN. To be fixed in analysis/preprocessing, likely a checksum or schema validation step.

504. How are analysis outputs linked to source datasets. DECIDED. Through the manifest and configuration references described in experiments/manifests/README.md and analysis/reproducibility/README.md.

Part XXXVIII, research integrity

505. What constitutes a failed experiment. UNKNOWN. To be fixed in experimental_protocol.md, expected to cover simulator crashes, logging faults or configuration errors, not inconvenient results.

506. Will failed experiments remain in the repository. DECIDED. Yes, per Rule 7 in CONTRIBUTING.md.

507. When can an experiment be excluded. DECIDED. Only when it meets a pre registered exclusion criterion fixed in experimental_protocol.md before the main campaign, per question 375.

508. Who determines exclusion. DECIDED. The pre registered criteria themselves, applied mechanically, not an individual judgement call made after seeing results.

509. When can a hypothesis be modified. DECIDED. Only before the relevant experiment is run, per Rule 6 in CONTRIBUTING.md, never after seeing inconvenient results.

510. What constitutes a post hoc analysis. DECIDED. Any analysis not specified in experimental_protocol.md before the data were collected.

511. How will exploratory results be labelled. DECIDED. Explicitly marked as exploratory in the relevant analysis notebook and in the paper, distinct from confirmatory results.

512. How will confirmatory results be labelled. DECIDED. As results that directly test a pre registered hypothesis using the pre registered method.

513. How will unexpected findings be handled. DECIDED. Reported openly as exploratory findings, and, where scientifically warranted, followed up with a new, explicitly pre registered confirmatory experiment rather than being folded into the existing confirmatory claims.

514. How will negative results be reported. DECIDED. Reported in full, with the same rigour as positive results, since a null hypothesis that survives testing is itself a scientifically important outcome for this project, per Rule 6 in CONTRIBUTING.md.

Part XXXIX, paper

515. What is the central claim of Paper 1. UNKNOWN. To be fixed once the main experimental campaign is complete, expected to concern whether a reproducible information boundary exists and what determines it.

516. What evidence is required. UNKNOWN. As set out in the success criteria in Part XLV.

517. What is the primary figure. UNKNOWN. Likely a boundary map or phase map from analysis/boundary_estimation, to be confirmed once the data exist.

518. What is the primary table. UNKNOWN. Likely a summary of boundary locations across the principal experimental conditions.

519. What is the central mathematical contribution. UNKNOWN. Depends on whether the candidate boundary function in theory/information_boundary.md survives contact with the data.

520. What are the limitations. UNKNOWN. To be documented honestly once known, expected to include simulator simplifications and the practical limits of physical validation.

521. What would make the paper unsuitable for publication. DECIDED. A central claim not supported by the pre registered evidence, an unacknowledged failure to survive the falsification tests in falsification_tests.md, or a novelty claim not supported by the literature review.

522. What additional experiments would reviewers likely request. UNKNOWN. To be anticipated once a draft exists, likely additional sensing modalities, larger N, or a stronger baseline.

Part XL, physical validation paper

523. What is scientifically new about the physical experiment. UNKNOWN. To be assessed once the physical validation results exist.

524. Is physical validation merely confirmation. UNKNOWN. To be assessed once the physical validation results exist; if it is merely confirmation of a simulation result, it belongs inside Paper 1 rather than becoming Paper 5.

525. Does it reveal phenomena absent from simulation. UNKNOWN. To be assessed once the physical validation results exist.

526. Does hardware introduce meaningful new variables. UNKNOWN. To be assessed once the physical validation results exist.

527. Is the physical result sufficiently independent to justify a separate paper. UNKNOWN. To be decided honestly once the results exist, per the explicit warning in papers/paper_05_physical_validation/paper.md against splitting one result into five thin papers merely to increase the paper count.

Part XLI, competition translation

528. What is the scientific contribution for ISEF. UNKNOWN. To be drawn directly from whatever Paper 1 concludes, once it exists, rather than written independently.

529. What is the engineering contribution. UNKNOWN. Expected to include the simulator, the estimator and controller implementations, and the physical validation platform.

530. What is the innovation contribution. UNKNOWN. To be drawn from novelty_matrix.md once complete.

531. What is the student's personal contribution. DECIDED as a process. Recorded continuously in competition/isef/student_contribution.md, not written retrospectively before judging.

532. What can be demonstrated physically. UNKNOWN. Depends on the outcome of Part XXXIII.

533. What can be explained mathematically. UNKNOWN. Depends on the outcome of theory/information_boundary.md.

534. What can be reproduced. DECIDED. Everything covered in Part XXXVI, that is, the simulation, the configuration, the seeds, the figures and the tables.

535. What limitations must be openly disclosed. UNKNOWN. As in question 520.

536. Which parts are competition specific rather than scientific. DECIDED. The ISEF forms, the Conrad business and humanitarian framing, and the WRO category mapping, all of which sit in competition/ and must not be allowed to distort the scientific content in research/, theory/, experiments/ or papers/, per Rule 20 in CONTRIBUTING.md.

Part XLII, personal contribution

537 to 545. What was personally designed, personally coded, personally derived mathematically, personally designed as experiments, personally analysed, personally integrated as hardware, which decisions were made by collaborators, what external infrastructure was used, and what would remain uniquely yours if the wider project disappeared. DECIDED as a process, not as a fixed answer here. These questions are answered on an ongoing basis in competition/isef/student_contribution.md, updated as work is actually done, rather than filled in speculatively before any of the work exists. Recording them honestly and continuously is treated as part of the scientific integrity of the project, not merely a competition formality.

Part XLIII, collaboration

546. What external expertise is required. UNKNOWN. To be identified as gaps become apparent during the literature review and theory work, likely candidates being estimation theory, RF engineering and UAV flight testing.

547. Why is it required. UNKNOWN. To be documented once identified.

548. What can be done independently. UNKNOWN. Expected to include most of research/, theory/, simulation/, algorithms/ and analysis/.

549. What must be done by a university or laboratory. UNKNOWN. Expected to include, at most, review of the physical testing plan and possibly access to flight facilities or specialist equipment.

550. What intellectual contribution will collaborators make. UNKNOWN. To be documented in competition/isef/student_contribution.md as it occurs.

551. What intellectual contribution will the student make. DECIDED as a process. Recorded continuously in competition/isef/student_contribution.md.

552. How will contributions be documented. DECIDED. In competition/isef/student_contribution.md, updated continuously.

553. How will authorship be handled. UNKNOWN. To be agreed explicitly with any collaborator before their contribution begins, not after the fact.

554. How will competition eligibility be protected. UNKNOWN. To be checked directly against the specific rules of ISEF, Conrad and WRO before any external collaboration is finalised, since eligibility rules differ between competitions and can be affected by the extent of external help.

Part XLIV, failure criteria

555. What would cause you to abandon the current research question. DECIDED. Clear, repeated evidence against H1, that is, no reproducible boundary of any kind, combined with no plausible alternative formulation surviving the literature review.

556. What result would show the central premise is wrong. DECIDED. A consistent failure to find any reproducible transition across the full range of information conditions tested, after ruling out the alternative explanations in Part XIV.

557. What result would show the effect is trivial. DECIDED. A boundary that is fully explained by a single, already well studied variable, such as connectivity alone, with no meaningful contribution from the joint combination of factors tested in H2.

558. What result would show it is already well established. DECIDED. A literature review finding that an equivalent joint boundary has already been characterised and shown to be shiftable by a decentralised controller, in a form that AeroNet's evidence does not meaningfully extend.

559. What result would show the controller provides no unique benefit. DECIDED. The boundary shift under AeroNet, H6, not being statistically distinguishable from the boundary under the best matched static baseline.

560. What result would show physical validation is unnecessary. DECIDED. Not applicable in the sense of making validation unnecessary in principle, since physical validation is part of the definition of a complete result for this project, but a result that shows the simulation is not sufficiently mature to generate a specific, falsifiable prediction would show that physical validation is premature rather than unnecessary.

561. What result would show the mathematical model is inadequate. DECIDED. The candidate boundary function in theory/information_boundary.md failing to fit the observed data meaningfully better than a simple baseline model with no interaction terms.

562. What result would justify changing the research question. DECIDED. Any of the failure results above, combined with a documented, literature supported alternative question that better fits what the evidence actually shows, agreed and recorded before further experimental work proceeds under the new question.

Part XLV, success criteria

563. What is the minimum scientifically meaningful result. DECIDED. A reproducible information boundary, confirmed under H1, with the alternative explanations in Part XIV properly ruled out.

564. What is the strongest scientifically meaningful result. DECIDED. The full outcome described in research_question.md under the contribution if everything works, that is, a characterised, mechanistically explained, mathematically modelled, scaling consistent, cross modality general, adaptively shiftable and physically validated boundary.

565. What evidence would establish a reproducible information boundary. DECIDED. Statistically significant, repeatable transition behaviour under H1, surviving the falsification tests in falsification_tests.md.

566. What evidence would establish that sensing, communication and geometry jointly determine it. DECIDED. Statistically significant interaction terms under H2.

567. What evidence would establish that adaptive reconfiguration shifts it. DECIDED. A statistically significant difference between the AeroNet boundary and the best matched static baseline boundary, under H6.

568. What evidence would establish scaling with N. DECIDED. A consistent, replicated relationship between swarm size and boundary location, under H7.

569. What evidence would establish cross modality generality. DECIDED. A reproducible boundary of similar qualitative character under a second sensing modality, under H8.

570. What evidence would establish physical validity. DECIDED. A physical experiment result consistent, within pre specified acceptable discrepancy, with a specific simulation prediction, under Part XXXIII.

571. What evidence would establish reproducibility. DECIDED. An independent researcher successfully reproducing the main conclusion using only the repository and its documentation, under Part XXXVI.

Part XLVI, final scientific audit

572. What is AeroNet actually trying to discover. Whether a reproducible information boundary separates stable from unstable decentralised collective estimation, and whether local reconfiguration can shift it.

573. What is the central hypothesis. That such a boundary exists, is jointly determined by sensing, communication, geometry and agent availability, and can be shifted by a decentralised, locally informed controller.

574. What is the central null hypothesis. That no reproducible critical boundary exists, as stated in H0-1.

575. What is the primary independent variable. Not yet fixed, a joint information condition drawn from sensing, communication, geometry and agent availability, with the exact primary variable to be confirmed in experimental_protocol.md.

576. What is the primary dependent variable. Not yet fixed, a collective estimation performance measure, to be confirmed in variables.md.

577. What is the primary metric. Not yet fixed, to be chosen in theory/information_boundary.md after the literature review.

578. What is the proposed information boundary. The candidate function B of sensing, communication, geometry, noise, packet loss, failed agent fraction and swarm size, set equal to zero, treated strictly as a candidate rather than a conclusion.

579. How will the boundary be detected. By fitting a transition model to collective estimation performance across systematically varied information conditions, and testing that fit against a smooth alternative, as set out in analysis/boundary_estimation.

580. What is the strongest competing explanation. That any apparent boundary is fully explained by network connectivity loss alone, as stated in H0-3.

581. How will that explanation be tested. By holding connectivity fixed while varying other information sources, and vice versa, as set out in falsification_tests.md.

582. What is the strongest relevant prior work. Not yet known, to be identified in literature_review.md.

583. What is genuinely different about AeroNet. Provisionally, the joint treatment of sensing, communication, geometry and agent availability as a single measurable information boundary, together with a test of whether a decentralised controller can shift that boundary rather than merely improve performance at a fixed point, subject to revision once the literature review is complete.

584. What would falsify the project. A consistent absence of any reproducible transition across the full range of information conditions tested, after the alternative explanations in Part XIV have been properly ruled out.

585. What is the first experiment. The simple baseline experiment, Experiment 1, using a fixed swarm size, fixed estimator, fixed geometry, fixed sensing and fixed communication policy, as set out in research_question.md.

586. What result would make you stop and reconsider the project. Any of the failure criteria listed in Part XLIV.

587. What result would justify implementing the adaptive AeroNet controller. A confirmed, reproducible boundary under H1 and H2, established before any adaptive control work begins.

588. What result would justify physical validation. A specific, falsifiable prediction from the simulation campaign that is worth the cost and risk of physical testing to check.

589. What result would justify a publication. The evidence set out in Part XLV being met to whatever degree it actually is, reported honestly, including where it falls short.

590. What exactly will you personally contribute. To be recorded continuously and specifically in competition/isef/student_contribution.md, not answered in the abstract here.

591. Can every major claim eventually be traced to evidence. This is a requirement of the repository structure itself, per Rule 1 and Rule 5 in CONTRIBUTING.md, and is checked, not assumed, throughout the project.

592. Can another researcher reproduce the entire result. This is the target set out in Part XXXVI, and is treated as unverified until an independent reproduction has actually been attempted.

Final gate

The checklist below mirrors the one in the original specification. It is not yet complete. Each box is to be ticked only once the corresponding document exists in full and has been reviewed, not merely started.

Research question frozen, not yet, drafted in research_question.md, to be frozen once reviewed.
Definitions frozen, not yet, drafted in research_question.md, several terms marked literature required above.
Hypotheses frozen, not yet, drafted in full in hypotheses.md, rationale and variable fields still to be completed following the literature review.
Null hypotheses defined, yes, in hypotheses.md.
Literature reviewed, not yet, literature_review.md is currently a template.
Closest prior work identified, not yet, depends on the literature review.
Novelty distinction documented, not yet, novelty_matrix.md is currently a template.
Variables defined, not yet, variables.md is currently a template.
Primary endpoint defined, not yet.
Secondary endpoints defined, not yet.
Experimental unit defined, not yet, provisional definition given above in Part XXVII.
Replication defined, not yet, pending pilot variance estimates.
Exclusion criteria defined, not yet.
Falsification tests defined, yes, in falsification_tests.md, with individual test detail still to be completed.
Mathematical state defined, not yet.
Observation model defined, not yet.
Communication model defined, not yet.
Sensing model defined, not yet.
Geometry model defined, not yet.
Estimator selected, not yet.
Information metric justified, not yet.
Candidate boundary defined, yes, as a candidate only, in research_question.md and theory/information_boundary.md.
Boundary detection method defined, not yet.
Baselines selected, not yet, candidate list only.
Simulator assumptions documented, not yet.
Simulator validation plan defined, yes, in simulation/validation/README.md, in outline.
Statistical analysis planned, not yet.
Scaling experiment defined, not yet, in outline only.
Ablation experiments defined, yes, in outline, in experiments/ablations/README.md.
Adversarial experiments defined, yes, in outline, in experiments/adversarial/README.md.
Physical validation target defined, not yet.
Hardware requirements defined, not yet.
Ground truth defined, not yet.
Safety and approval requirements identified, not yet.
Data structure defined, yes, in outline, in the experiments/ folder structure and manifest fields.
Reproducibility procedure defined, yes, in outline, in analysis/reproducibility/README.md and CONTRIBUTING.md.
Personal contribution defined, yes, as a process, in competition/isef/student_contribution.md.

Only once every box above is genuinely ticked should work move into turning theory/ into full mathematics and building the simulator.
