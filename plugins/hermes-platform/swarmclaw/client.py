from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class SwarmClawAdapterError(RuntimeError):
    """Ошибка private-протокола между Hermes Platform и SwarmClaw."""


@dataclass(frozen=True)
class SwarmClawExecutionRequest:
    gateway_task_id: str
    provider_connection_id: str
    organization_id: str
    workspace_id: str | None
    project_id: str | None
    user_id: str
    input: str
    instructions: str


@dataclass(frozen=True)
class SwarmClawExecution:
    execution_id: str
    status: str
    output: str | None = None
    error: str | None = None


class SwarmClawClient:
    """Клиент закрытого API SwarmClaw; OAuth-данные через него не передаются."""

    def __init__(self, base_url: str, service_key: str, timeout_seconds: float = 10.0) -> None:
        normalized_url = base_url.rstrip("/")
        if not normalized_url.startswith(("http://", "https://")):
            raise ValueError("HERMES_SWARMCLAW_BASE_URL must be an HTTP(S) URL")
        if not service_key:
            raise ValueError("HERMES_SWARMCLAW_SERVICE_KEY is required")
        self._base_url = normalized_url
        self._service_key = service_key
        self._timeout_seconds = timeout_seconds

    @classmethod
    def from_environment(cls) -> SwarmClawClient:
        base_url = os.environ.get("HERMES_SWARMCLAW_BASE_URL", "")
        service_key = os.environ.get("HERMES_SWARMCLAW_SERVICE_KEY", "")
        return cls(base_url=base_url, service_key=service_key)

    def create_execution(self, request: SwarmClawExecutionRequest) -> SwarmClawExecution:
        payload = {
            "gatewayTaskId": request.gateway_task_id,
            "providerConnectionId": request.provider_connection_id,
            "organizationId": request.organization_id,
            "workspaceId": request.workspace_id,
            "projectId": request.project_id,
            "userId": request.user_id,
            "input": request.input,
            "instructions": request.instructions,
        }
        return self._to_execution(self._request("POST", "/api/internal/hermes/executions", payload))

    def get_execution(self, execution_id: str) -> SwarmClawExecution:
        return self._to_execution(
            self._request("GET", f"/api/internal/hermes/executions/{execution_id}")
        )

    def stop_execution(self, execution_id: str) -> SwarmClawExecution:
        return self._to_execution(
            self._request("POST", f"/api/internal/hermes/executions/{execution_id}/stop")
        )

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, object] | None = None,
    ) -> dict[str, object]:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(
            url=f"{self._base_url}{path}",
            data=data,
            method=method,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Hermes-Service-Key": self._service_key,
            },
        )
        try:
            with urlopen(request, timeout=self._timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as error:
            raise SwarmClawAdapterError(
                f"SwarmClaw private API returned HTTP {error.code}"
            ) from error
        except URLError as error:
            raise SwarmClawAdapterError("SwarmClaw private API is unavailable") from error

        try:
            decoded = json.loads(body)
        except json.JSONDecodeError as error:
            raise SwarmClawAdapterError("SwarmClaw private API returned invalid JSON") from error

        if not isinstance(decoded, dict):
            raise SwarmClawAdapterError("SwarmClaw private API returned an invalid response")
        return cast(dict[str, object], decoded)

    @staticmethod
    def _to_execution(payload: dict[str, object]) -> SwarmClawExecution:
        execution_id = payload.get("executionId")
        status = payload.get("status")
        if not isinstance(execution_id, str) or not isinstance(status, str):
            raise SwarmClawAdapterError("SwarmClaw private API returned an invalid execution")

        output = payload.get("output")
        error = payload.get("error")
        return SwarmClawExecution(
            execution_id=execution_id,
            status=status,
            output=output if isinstance(output, str) else None,
            error=error if isinstance(error, str) else None,
        )
