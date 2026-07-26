from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path


def _run(cmd):
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return True, (result.stdout or result.stderr).splitlines()[0]
        return False, result.stderr.strip() or "Command failed"
    except Exception as e:
        return False, str(e)


def check_python():
    return ("Python", True, platform.python_version())


def check_platform():
    return ("Platform", True, f"{platform.system()} {platform.release()}")


def check_hermes_home():
    home = Path.home() / ".hermes"
    return ("HERMES_HOME", home.exists(), str(home))


def check_git():
    ok, out = _run(["git", "--version"])
    return ("Git", ok, out)


def check_docker():
    ok, out = _run(["docker", "info"])
    return ("Docker", ok, "Running" if ok else out)


def check_docker_compose():
    ok, out = _run(["docker", "compose", "version"])
    return ("Docker Compose", ok, out)


def check_uv():
    uv = shutil.which("uv")
    if uv:
        ok, out = _run([uv, "--version"])
        return ("uv", ok, out)

    hermes_uv = Path.home() / ".hermes" / "bin" / "uv"
    if hermes_uv.exists():
        ok, out = _run([str(hermes_uv), "--version"])
        return ("uv", ok, out)

    return ("uv", False, "Not found")


def check_node():
    ok, out = _run(["node", "--version"])
    return ("Node", ok, out)


def check_npm():
    ok, out = _run(["npm", "--version"])
    return ("npm", ok, out)


def check_ffmpeg():
    ok, out = _run(["ffmpeg", "-version"])
    return ("ffmpeg", ok, out)


def check_ripgrep():
    ok, out = _run(["rg", "--version"])
    return ("ripgrep", ok, out)
