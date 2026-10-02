from __future__ import annotations

import math
from collections import defaultdict


def aggregate(trajectory: list[dict], packets: list[dict]) -> list[dict]:
    by_agent = defaultdict(list)

    for row in trajectory:
        by_agent[int(row["agent_id"])].append(row)

    delivered = sum(int(p["delivered"]) for p in packets)
    total = len(packets)

    loss_rate = (
        1.0 - delivered / total
        if total
        else 0.0
    )

    output = []

    for agent_id, rows in sorted(by_agent.items()):
        errors = [float(r["position_error"]) for r in rows]
        squared = [float(r["squared_error"]) for r in rows]
        traces = [float(r["covariance_trace"]) for r in rows]

        output.append(
            {
                "agent_id": agent_id,
                "rmse": math.sqrt(sum(squared) / len(squared)),
                "mae": sum(errors) / len(errors),
                "final_error": errors[-1],
                "mean_covariance_trace": sum(traces) / len(traces),
                "final_covariance_trace": traces[-1],
                "number_of_steps": len(rows),
                "packets_generated": total,
                "packets_delivered": delivered,
                "realised_loss_rate": loss_rate,
            }
        )

    return output
