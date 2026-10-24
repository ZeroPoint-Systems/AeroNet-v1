import numpy as np


class Policy:
    name = "base"

    def __init__(self, agents, budget, steps):
        self.budget = int(budget)
        self.used = np.zeros(agents, dtype=int)
        self.last_sent = np.full(agents, -10**9, dtype=int)
        self.previous_score = np.zeros(agents)
        self.trend = np.zeros(agents)
        self.interval = max(1, int(np.ceil(steps / max(1, self.budget))))

    def decide(self, i, step, filt):
        raise NotImplementedError

    def can_send(self, i):
        return self.used[i] < self.budget

    def stale(self, i, step):
        # Ensures event-triggered policies do not silently spend far less
        # than the available budget solely because no trigger fires.
        return step - self.last_sent[i] >= self.interval

    def record(self, i, step):
        if not self.can_send(i):
            raise RuntimeError("Communication budget exceeded")
        self.used[i] += 1
        self.last_sent[i] = step


class NoCommunication(Policy):
    name = "none"

    def __init__(self, agents, budget, steps):
        super().__init__(agents, budget, steps)

    def decide(self, i, step, filt):
        return False


class Periodic(Policy):
    name = "periodic"

    def __init__(self, agents, budget, steps):
        super().__init__(agents, budget, steps)

    def decide(self, i, step, filt):
        return self.can_send(i) and self.stale(i, step)


class Reactive(Policy):
    name = "reactive"

    def __init__(self, agents, budget, threshold, steps):
        super().__init__(agents, budget, steps)
        self.threshold = float(threshold)

    def decide(self, i, step, filt):
        trigger = filt.innovation_norm >= self.threshold
        return self.can_send(i) and (trigger or self.stale(i, step))


class Predictive(Policy):
    name = "predictive"

    def __init__(self, agents, budget, threshold, horizon, steps):
        super().__init__(agents, budget, steps)
        self.threshold = float(threshold)
        self.horizon = int(horizon)

    def predict_score(self, i, score):
        trend = 0.75 * self.trend[i] + 0.25 * (
            score - self.previous_score[i]
        )
        self.trend[i] = trend
        self.previous_score[i] = score
        return max(0.0, score + self.horizon * trend)

    def decide(self, i, step, filt):
        predicted = self.predict_score(i, filt.innovation_norm)
        return self.can_send(i) and (
            predicted >= self.threshold or self.stale(i, step)
        )


def build_policies(config):
    return [
        NoCommunication(
            config.agents, config.communication_budget_per_agent, config.steps
        ),
        Periodic(
            config.agents, config.communication_budget_per_agent, config.steps
        ),
        Reactive(
            config.agents, config.communication_budget_per_agent,
            config.reactive_threshold, config.steps
        ),
        Predictive(
            config.agents, config.communication_budget_per_agent,
            config.warning_threshold, config.prediction_horizon, config.steps
        ),
    ]
