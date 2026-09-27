"""Pytest configuration: ensure the repository root is importable as the
source root, so that test modules can use `import simulation...` and
`import analysis...` regardless of which directory pytest is invoked from.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
