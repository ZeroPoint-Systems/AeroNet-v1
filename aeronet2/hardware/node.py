"""One physical/virtual estimation node (UDP). Uses the *same* InfoFilter and AgentPolicy as the simulator,
so hardware results are directly comparable with simulation.

Replace `read_sensor` with a real sensor driver (and `truth` with an independent reference) for the
physical experiment. All nodes share a wall-clock epoch `--t0`; for multi-device runs synchronise clocks
(chrony/NTP on a LAN, or PTP) and log the measured offset, otherwise one-way latencies are meaningless.
"""
from __future__ import annotations

import argparse, csv, os, queue, socket, struct, threading, time

import numpy as np

from aeronet2.fusion import InfoFilter
from aeronet2.model import Scenario, sensor_R, simulate_truth
from aeronet2.network import adjacency
from aeronet2.policies import AgentPolicy
from aeronet2.rng import rng_for

HDR = struct.Struct("!BBIB")      # src, dst, t_send(step), kind
BODY = struct.Struct("!12d")      # z[2] + upper-triangular covariance[10]
IU = np.triu_indices(4)


def pack(src, dst, t, z, P) -> bytes:
    return HDR.pack(src, dst, t, 0) + BODY.pack(*z, *P[IU])


def unpack(b: bytes):
    src, dst, t, _ = HDR.unpack_from(b)
    v = BODY.unpack_from(b, HDR.size)
    P = np.zeros((4, 4)); P[IU] = v[2:]
    return src, dst, t, np.array(v[:2]), P + P.T - np.diag(np.diag(P))


def main(a):
    sc = Scenario(n_agents=a.n, steps=a.steps, burn_in=a.burn_in, budget=a.budget, topology=a.topology,
                  q=a.q, anisotropy=a.anisotropy, manoeuvre_rate=a.manoeuvre_rate, loss=a.loss)
    me = a.id
    nb = adjacency(sc.topology, sc.n_agents)[me]
    truth = simulate_truth(sc, a.seed)                     # stands in for the physical target
    L = np.linalg.cholesky(sensor_R(sc)[me]); srng = rng_for(a.seed, "sensor", me)
    emul = np.random.default_rng([a.seed, 99, me])
    flt, pol = InfoFilter(sc, me), AgentPolicy(a.policy, sc, me, nb, a.seed, lambda i, j: 1.0 - a.loss)

    def read_sensor(k):                                    # <-- replace with a real driver
        return truth[k, :2] + L @ srng.standard_normal(2)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((a.host, a.base_port + me)); sock.settimeout(0.05)
    rx: "queue.Queue" = queue.Queue(); stop = threading.Event()

    def rx_loop():
        while not stop.is_set():
            try:
                data, _ = sock.recvfrom(2048)
                rx.put((data, time.time()))
            except socket.timeout:
                pass
    threading.Thread(target=rx_loop, daemon=True).start()

    os.makedirs(a.out, exist_ok=True)
    f1 = open(os.path.join(a.out, f"node{me}.csv"), "w", newline=""); w1 = csv.writer(f1)
    w1.writerow(["step", "t_wall", "est_x", "est_y", "trP", "sent", "dst", "rx_total", "lateness_s"])
    f2 = open(os.path.join(a.out, f"rx{me}.csv"), "w", newline=""); w2 = csv.writer(f2)
    w2.writerow(["src", "t_send_step", "t_recv_step", "latency_s", "bytes"])
    rx_total = 0
    for k in range(sc.steps):
        due = a.t0 + k * a.dt
        time.sleep(max(0.0, due - time.time()))
        late = time.time() - due
        z_k = read_sensor(k)
        flt.observe(k, z_k)
        pol.on_step(flt.last_innovation)
        while True:
            try:
                data, tr = rx.get_nowait()
            except queue.Empty:
                break
            src, _, ts, z, P = unpack(data)
            ts = min(ts, k)
            flt.receive(src, ts, z, k); pol.on_gossip(src, P, k - ts)
            rx_total += 1
            w2.writerow([src, ts, k, tr - (a.t0 + ts * a.dt), len(data)])
        sent, dst = 0, -1
        for j in pol.decide(k, flt, True):
            x, P = flt.estimate()
            pkt = pack(me, j, k, z_k, P)
            sent, dst = 1, j
            pol.after_send(j, x[:2])
            if emul.random() < a.emulate_loss:
                continue
            dest = (a.host, a.base_port + j)
            if a.emulate_delay_ms > 0:
                threading.Timer(a.emulate_delay_ms / 1000.0 * (0.5 + emul.random()), sock.sendto, (pkt, dest)).start()
            else:
                sock.sendto(pkt, dest)
        x, P = flt.estimate()
        w1.writerow([k, time.time(), x[0], x[1], float(np.trace(P)), sent, dst, rx_total, late])
    time.sleep(0.3); stop.set(); f1.close(); f2.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", type=int, required=True); ap.add_argument("--n", type=int, default=4)
    ap.add_argument("--steps", type=int, default=120); ap.add_argument("--burn-in", type=int, default=20)
    ap.add_argument("--dt", type=float, default=0.05); ap.add_argument("--t0", type=float, required=True)
    ap.add_argument("--policy", default="periodic"); ap.add_argument("--budget", type=int, default=20)
    ap.add_argument("--topology", default="ring"); ap.add_argument("--q", type=float, default=0.01)
    ap.add_argument("--anisotropy", type=float, default=6.0); ap.add_argument("--manoeuvre-rate", type=float, default=0.0)
    ap.add_argument("--loss", type=float, default=0.1); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--host", default="127.0.0.1"); ap.add_argument("--base-port", type=int, default=24100)
    ap.add_argument("--emulate-loss", type=float, default=0.0); ap.add_argument("--emulate-delay-ms", type=float, default=0.0)
    ap.add_argument("--out", default="hw_logs")
    main(ap.parse_args())
