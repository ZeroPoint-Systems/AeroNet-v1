import argparse
import csv
import json
import math
import multiprocessing as mp
import random
import socket
import statistics
import time
from pathlib import Path


def truth_at(step):
    t = step * 0.02
    return 20.0 + 0.08 * step, 10.0 + 4.0 * math.sin(t * 0.9)


def agent_process(agent_id, ports, steps, dt, loss, seed, policy, queue):
    sensor_rng = random.Random(seed + agent_id * 1009)
    network_rng = random.Random(seed + 1000003 + agent_id * 2003)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", ports[agent_id]))
    sock.setblocking(False)

    estimate = [0.0, 0.0]
    variance = [100.0, 100.0]
    latest_peer = {}
    last_broadcast = -999
    sent = received = accepted = stale = 0

    try:
        time.sleep(0.04 * agent_id)

        for step in range(steps):
            tx, ty = truth_at(step)
            sigma = 2.0 + agent_id * 0.15
            measurement = [
                tx + sensor_rng.gauss(0, sigma),
                ty + sensor_rng.gauss(0, sigma)
            ]
            measurement_var = sigma * sigma

            # Local Kalman update using this agent's own sensor only.
            for axis in range(2):
                prior_var = variance[axis] + 0.05
                gain = prior_var / (prior_var + measurement_var)
                estimate[axis] += gain * (measurement[axis] - estimate[axis])
                variance[axis] = (1.0 - gain) * prior_var

            # Retain only newer messages from each peer.
            while True:
                try:
                    payload, _ = sock.recvfrom(4096)
                except BlockingIOError:
                    break
                except ConnectionResetError:
                    continue

                try:
                    msg = json.loads(payload.decode("utf-8"))
                    sender = int(msg["agent_id"])
                    msg_step = int(msg["step"])
                    peer_est = [float(v) for v in msg["estimate"]]
                except (ValueError, TypeError, KeyError, json.JSONDecodeError):
                    continue

                if sender == agent_id:
                    continue
                received += 1

                # Reject future and stale information.
                if msg_step > step or step - msg_step > 3:
                    stale += 1
                    continue

                previous = latest_peer.get(sender)
                if previous is not None and msg_step <= previous[0]:
                    continue

                latest_peer[sender] = (msg_step, peer_est)
                accepted += 1

            fresh = [
                value for msg_step, value in latest_peer.values()
                if 0 <= step - msg_step <= 3
            ]

            # One bounded consensus correction per step. Peer estimates are
            # not treated as independent measurements and do not alter variance.
            if fresh:
                for axis in range(2):
                    peer_mean = sum(p[axis] for p in fresh) / len(fresh)
                    estimate[axis] += 0.08 * (peer_mean - estimate[axis])

            if policy == "none":
                send_now = False
            elif policy == "periodic":
                send_now = True
            else:
                send_now = step - last_broadcast >= 3

            if send_now:
                message = json.dumps({
                    "agent_id": agent_id,
                    "step": step,
                    "estimate": estimate
                }).encode("utf-8")

                for peer_id, port in enumerate(ports):
                    if peer_id == agent_id or network_rng.random() < loss:
                        continue
                    try:
                        sock.sendto(message, ("127.0.0.1", port))
                        sent += 1
                    except OSError:
                        pass

                last_broadcast = step

            error = math.hypot(estimate[0] - tx, estimate[1] - ty)
            queue.put({
                "agent_id": agent_id,
                "step": step,
                "truth_x": tx,
                "truth_y": ty,
                "estimate_x": estimate[0],
                "estimate_y": estimate[1],
                "position_error": error,
                "messages_sent_cumulative": sent,
                "messages_received_cumulative": received,
                "messages_accepted_cumulative": accepted,
                "messages_stale_cumulative": stale,
                "policy": policy,
                "seed": seed
            })
            time.sleep(dt)
    finally:
        sock.close()


def run_trial(root, policy, seed, agents, steps, dt, loss):
    folder = root / f"seed_{seed}_{policy}"
    folder.mkdir(parents=True, exist_ok=True)
    ports = [24000 + i for i in range(agents)]
    ctx = mp.get_context("spawn")
    queue = ctx.Queue()
    processes = [
        ctx.Process(
            target=agent_process,
            args=(i, ports, steps, dt, loss, seed, policy, queue)
        )
        for i in range(agents)
    ]

    start = time.perf_counter()
    for process in processes:
        process.start()

    rows = []
    expected = agents * steps
    deadline = time.time() + max(30, agents * steps * dt + 20)

    while len(rows) < expected and time.time() < deadline:
        try:
            rows.append(queue.get(timeout=0.5))
        except Exception:
            if all(not p.is_alive() for p in processes):
                break

    for process in processes:
        process.join(timeout=3)
        if process.is_alive():
            process.terminate()
            process.join()

    rows.sort(key=lambda r: (r["agent_id"], r["step"]))
    if rows:
        with (folder / "agent_trace.csv").open(
            "w", newline="", encoding="utf-8"
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    errors = [r["position_error"] for r in rows]
    summary = {
        "policy": policy,
        "seed": seed,
        "trace_rows": len(rows),
        "expected_trace_rows": expected,
        "mean_position_error": statistics.mean(errors) if errors else None,
        "messages_sent_total": (
            sum(r["messages_sent_cumulative"] for r in rows) if rows else 0
        ),
        "process_exit_codes": [p.exitcode for p in processes],
        "wall_time_seconds": round(time.perf_counter() - start, 3),
        "status": (
            "PASS"
            if len(rows) == expected
            and all(p.exitcode == 0 for p in processes)
            else "FAIL"
        ),
        "trace_csv": str((folder / "agent_trace.csv").resolve())
    }

    (folder / "summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    if summary["status"] != "PASS":
        raise RuntimeError(f"Trial failed: {summary}")

    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents", type=int, default=4)
    parser.add_argument("--steps", type=int, default=200)
    parser.add_argument("--dt", type=float, default=0.005)
    parser.add_argument("--loss", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=20261023)
    parser.add_argument("--batch-seeds", type=int, default=20)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    if args.agents < 2 or args.steps < 1 or not 0 <= args.loss < 1:
        parser.error("Require agents >= 2, steps >= 1 and loss in [0,1).")

    root = Path(args.output).resolve()
    root.mkdir(parents=True, exist_ok=True)
    summaries = []

    for seed in range(args.seed, args.seed + args.batch_seeds):
        for policy in ("none", "periodic", "adaptive"):
            print(f"Running {policy}, seed {seed}", flush=True)
            summaries.append(run_trial(
                root, policy, seed, args.agents, args.steps, args.dt, args.loss
            ))

    aggregates = []
    for policy in ("none", "periodic", "adaptive"):
        group = [s for s in summaries if s["policy"] == policy]
        errors = [s["mean_position_error"] for s in group]
        packets = [s["messages_sent_total"] for s in group]
        aggregates.append({
            "policy": policy,
            "seeds": len(group),
            "mean_position_error_across_seeds": statistics.mean(errors),
            "sd_between_seed_errors": (
                statistics.stdev(errors) if len(errors) > 1 else 0.0
            ),
            "mean_messages_sent_total": statistics.mean(packets),
            "all_trials_passed": all(s["status"] == "PASS" for s in group)
        })

    with (root / "benchmark_summary.csv").open(
        "w", newline="", encoding="utf-8"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(aggregates[0]))
        writer.writeheader()
        writer.writerows(aggregates)

    (root / "benchmark_summary.json").write_text(
        json.dumps({
            "configuration": vars(args),
            "policies": aggregates,
            "trials": summaries
        }, indent=2),
        encoding="utf-8"
    )

    print(json.dumps({
        "status": "PASS",
        "trials_completed": len(summaries),
        "summary_csv": str((root / "benchmark_summary.csv").resolve()),
        "policies": aggregates
    }, indent=2))


if __name__ == "__main__":
    mp.freeze_support()
    main()
