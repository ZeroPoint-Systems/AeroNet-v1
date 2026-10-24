import numpy as np


class CommunicationNetwork:
    """Fixed ring topology with reproducible outages, losses and delays."""

    def __init__(self, config, seed):
        self.config = config
        self.agents = config.agents
        self.steps = config.steps
        rng = np.random.default_rng(seed)

        n, steps = self.agents, self.steps
        self.active = np.ones((steps, n), dtype=bool)
        self.loss = rng.random((steps, n, n)) < config.packet_loss
        self.delay = np.zeros((steps, n, n), dtype=int)

        delayed = rng.random((steps, n, n)) < config.delay_probability
        if config.max_delay > 0 and delayed.any():
            self.delay[delayed] = rng.integers(
                1, config.max_delay + 1, size=int(delayed.sum())
            )

        self.link = np.zeros((n, n), dtype=bool)
        for i in range(n):
            self.link[i, (i - 1) % n] = True
            self.link[i, (i + 1) % n] = True
        np.fill_diagonal(self.link, False)

        # Avoid duplicate neighbours in a two-agent network.
        self._neighbours = []
        for i in range(n):
            self._neighbours.append(tuple(
                j for j in ((i - 1) % n, (i + 1) % n)
                if j != i
            ))
        self._neighbours = [
            tuple(dict.fromkeys(items)) for items in self._neighbours
        ]

        # Exogenous outages, shared by policies for a given seed.
        for i in range(n):
            t = 0
            while t < steps:
                if rng.random() < config.disconnect_probability:
                    duration = int(rng.integers(
                        config.disconnect_min_steps,
                        config.disconnect_max_steps + 1
                    ))
                    self.active[t:min(steps, t + duration), i] = False
                    t += duration
                else:
                    t += 1

        self.sent = 0
        self.delivered = 0
        self.dropped = 0
        self.bytes_sent = 0

    def neighbours(self, sender):
        return self._neighbours[sender]

    def transmit(self, step, sender, receiver, state, pending):
        """Attempt one packet. Delivery is counted only at actual arrival."""
        self.sent += 1
        self.bytes_sent += int(np.asarray(state).nbytes)

        if not self.link[sender, receiver]:
            self.dropped += 1
            return False

        if not self.active[step, sender] or not self.active[step, receiver]:
            self.dropped += 1
            return False

        if self.loss[step, sender, receiver]:
            self.dropped += 1
            return False

        # Messages are delivered no earlier than the next simulation step.
        # This prevents packets being queued after the current inbox is popped.
        extra_delay = int(self.delay[step, sender, receiver])
        arrival = step + max(1, extra_delay)

        if arrival >= self.steps:
            self.dropped += 1
            return False

        pending[arrival].append(
            (receiver, sender, np.asarray(state).copy(), step)
        )
        return True
