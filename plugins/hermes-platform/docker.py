from __future__ import annotations

import json
import subprocess


def docker_running():
    try:
        subprocess.run(
            ["docker", "info"],
            check=True,
            capture_output=True,
            timeout=5,
        )
        return True
    except Exception:
        return False


def hermes_containers():
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "--format",
                "{{json .}}",
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
        )

        containers = []

        for line in result.stdout.splitlines():
            if not line.strip():
                continue

            c = json.loads(line)

            if c["Names"].startswith("hermes-"):
                containers.append(
                    (
                        c["Names"],
                        c["Image"],
                        c["Status"],
                    )
                )

        return containers

    except Exception:
        return []
