from .client import get


def swarm_status():
    code, body = get("/")

    if code is None:
        return False, body

    return True, f"HTTP {code}"
