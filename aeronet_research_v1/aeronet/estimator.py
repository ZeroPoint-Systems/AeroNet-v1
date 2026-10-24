import numpy as np
from .model import measurement_matrix, process_covariance, transition_matrix


class LocalKalmanFilter:
    """Local constant-velocity Kalman filter with bounded peer-state correction."""
    def __init__(self, dt, process_noise, measurement_noise, consensus_gain=0.08):
        self.F = transition_matrix(dt)
        self.Q = process_covariance(dt, process_noise)
        self.H = measurement_matrix()
        self.R = np.eye(2) * float(measurement_noise)
        self.x = np.zeros(4, dtype=float)
        self.P = np.eye(4, dtype=float) * 10.0
        self.consensus_gain = float(consensus_gain)
        self.innovation = np.zeros(2)
        self.innovation_norm = 0.0

    def predict(self):
        self.x = self.F @ self.x
        self.P = self.F @ self.P @ self.F.T + self.Q
        self.P = (self.P + self.P.T) * 0.5

    def update(self, z):
        z = np.asarray(z, dtype=float)
        residual = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + self.R
        K = np.linalg.solve(S, self.H @ self.P).T
        self.x = self.x + K @ residual
        A = np.eye(4) - K @ self.H
        self.P = A @ self.P @ A.T + K @ self.R @ K.T
        self.P = (self.P + self.P.T) * 0.5
        self.innovation = residual
        self.innovation_norm = float(np.sqrt(max(residual @ np.linalg.solve(S, residual), 0.0)))

    def consensus(self, peer_states):
        if len(peer_states) == 0:
            return
        peer_mean = np.mean(np.asarray(peer_states, dtype=float), axis=0)
        self.x += self.consensus_gain * np.clip(peer_mean - self.x, -2.0, 2.0)
        # Peer estimates are correlated suggestions, not independent observations.
        # Therefore this correction deliberately does not shrink covariance.
