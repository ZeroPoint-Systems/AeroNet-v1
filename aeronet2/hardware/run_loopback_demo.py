"""Loopback end-to-end check of the hardware code path (4 processes, UDP, emulated loss/delay).

This is a *software-in-the-loop* test, not physical validation: it proves the node code, wire format,
logging and analysis pipeline work before you move to real devices and real sensors.
"""
import os, subprocess, sys, time, csv, shutil
import numpy as np
from aeronet2.model import Scenario, simulate_truth

N, STEPS, DT, SEED = 4, 100, 0.05, 7
HERE = os.path.dirname(os.path.abspath(__file__))


def run(policy, out, extra=()):
    shutil.rmtree(out, ignore_errors=True)
    t0 = time.time() + 1.5
    procs = [subprocess.Popen([sys.executable, os.path.join(HERE, "node.py"), "--id", str(i), "--n", str(N), "--steps", str(STEPS),
                               "--dt", str(DT), "--t0", str(t0), "--policy", policy, "--seed", str(SEED), "--out", out,
                               "--base-port", str(24100 + {"none": 0, "periodic": 10, "voi_psa": 20}.get(policy, 30)), "--emulate-loss", "0.1",
                               "--emulate-delay-ms", "40", *extra]) for i in range(N)]
    for p in procs:
        p.wait(timeout=60)
    sc = Scenario(n_agents=N, steps=STEPS, q=0.01, anisotropy=6.0)
    truth = simulate_truth(sc, SEED)
    err, sent, rx, lat = [], 0, 0, []
    for i in range(N):
        rows = list(csv.DictReader(open(os.path.join(out, f"node{i}.csv"))))
        for r in rows:
            k = int(r["step"]); sent += int(r["sent"])
            if k >= 20:
                err.append((float(r["est_x"]) - truth[k, 0]) ** 2 + (float(r["est_y"]) - truth[k, 1]) ** 2)
        for r in csv.DictReader(open(os.path.join(out, f"rx{i}.csv"))):
            rx += 1; lat.append(float(r["latency_s"]))
    return dict(policy=policy, rmse=float(np.sqrt(np.mean(err))), sent=sent, received=rx,
                median_latency_ms=1000 * float(np.median(lat)) if lat else float("nan"))


if __name__ == "__main__":
    for pol in ("none", "periodic", "voi_psa"):
        print(run(pol, os.path.join(HERE, "hw_logs", pol)), flush=True)
