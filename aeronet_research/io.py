from __future__ import annotations

import csv
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any


def git_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def stable_seed(base_seed: int, index: int) -> int:
    value = f"{base_seed}:{index}".encode()
    digest = hashlib.sha256(value).digest()
    return int.from_bytes(digest[:4], "big")


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fields = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def provenance() -> dict[str, str]:
    try:
        import numpy
        numpy_version = numpy.__version__
    except Exception:
        numpy_version = "unknown"

    return {
        "git_commit": git_commit(),
        "software_version": "1.0.0",
        "python_version": sys.version,
        "platform": platform.platform(),
        "numpy_version": numpy_version,
    }
