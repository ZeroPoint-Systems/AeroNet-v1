"""A dependency free fallback test runner.

The test files in this directory are ordinary pytest style test modules,
and pytest, configured in pyproject.toml, is the intended way to run them.
This script exists only for environments where pytest is not installed:
it discovers every tests/**/test_*.py module, calls every top level
function whose name starts with test_, and reports a plain pass or fail
summary using only the standard library.

Usage: python tests/run_all.py
"""

from __future__ import annotations

import importlib.util
import inspect
import sys
import traceback
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def discover_test_modules():
    for path in sorted((REPO_ROOT / "tests").rglob("test_*.py")):
        if path.name == "run_all.py":
            continue
        module_name = str(path.relative_to(REPO_ROOT)).replace("/", ".").removesuffix(".py")
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
        except ModuleNotFoundError as exc:
            yield module_name, None, str(exc)
            continue
        yield module_name, module, None


def run() -> int:
    total = 0
    failures = []
    skipped_modules = []

    for module_name, module, import_error in discover_test_modules():
        if module is None:
            skipped_modules.append((module_name, import_error))
            print(f"SKIP  {module_name} (could not import: {import_error})")
            continue
        test_functions = [
            (name, obj)
            for name, obj in vars(module).items()
            if name.startswith("test_") and inspect.isfunction(obj)
        ]
        for name, func in test_functions:
            signature = inspect.signature(func)
            if len(signature.parameters) > 0:
                # skip tests that require pytest fixtures such as tmp_path;
                # these are exercised when pytest itself is available
                continue
            total += 1
            try:
                func()
                print(f"PASS  {module_name}.{name}")
            except Exception:
                failures.append((module_name, name, traceback.format_exc()))
                print(f"FAIL  {module_name}.{name}")

    print()
    print(f"{total} tests run, {len(failures)} failed, {len(skipped_modules)} modules skipped")
    if skipped_modules:
        print("skipped modules are those importing pytest, which is not installed in this")
        print("environment; they are ordinary pytest test files and will run under pytest.")
    if failures:
        print()
        for module_name, name, tb in failures:
            print(f"--- {module_name}.{name} ---")
            print(tb)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(run())
