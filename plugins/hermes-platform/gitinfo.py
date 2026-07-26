from __future__ import annotations

import subprocess
from pathlib import Path


REPOS = {
    "hermes-platform": Path.home() / "hermes" / "hermes-platform",
    "hermes-agent": Path.home() / ".hermes" / "hermes-agent",
}


def _run(repo: Path, *args):
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def repo_status():
    result = []

    for name, path in REPOS.items():

        if not path.exists():
            result.append((name, False, "missing"))
            continue

        branch = _run(path, "branch", "--show-current").stdout.strip()

        dirty = bool(_run(path, "status", "--porcelain").stdout.strip())

        state = "modified" if dirty else "clean"

        result.append((name, True, f"{branch} ({state})"))

    return result
