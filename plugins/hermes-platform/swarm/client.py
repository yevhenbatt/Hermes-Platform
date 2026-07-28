from __future__ import annotations

import requests

BASE_URL = "http://127.0.0.1:3456"


def get(path: str):
    url = BASE_URL.rstrip("/") + path

    try:
        response = requests.get(url, timeout=3)
        return response.status_code, response.text
    except Exception as exc:
        return None, str(exc)
