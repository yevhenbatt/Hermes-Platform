from __future__ import annotations

import json
import subprocess


CONTAINERS = {
    "Traefik": "hermes-traefik",
    "PostgreSQL": "hermes-postgres",
    "Valkey": "hermes-valkey",
    "Ollama": "hermes-ollama",
    "n8n": "hermes-n8n",
    "Portainer": "hermes-portainer",
}


def _inspect(container: str):
    try:
        result = subprocess.run(
            [
                "docker",
                "inspect",
                container,
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=5,
        )

        data = json.loads(result.stdout)[0]

        state = data["State"]

        running = state.get("Running", False)

        health = state.get("Health")

        if health:
            return running and health["Status"] == "healthy", health["Status"]

        return running, "running" if running else "stopped"

    except Exception as e:
        return False, str(e)


def service_checks():
    results = []

    for service, container in CONTAINERS.items():
        ok, status = _inspect(container)
        results.append((service, ok, status))

    return results
