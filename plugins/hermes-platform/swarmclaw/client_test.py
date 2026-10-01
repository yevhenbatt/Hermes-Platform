from __future__ import annotations

import json
import unittest
from unittest.mock import patch

from client import SwarmClawClient, SwarmClawExecutionRequest


class FakeResponse:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self._payload).encode("utf-8")


class SwarmClawClientTest(unittest.TestCase):
    @patch("client.urlopen")
    def test_create_execution_sends_only_task_context_and_service_key(self, urlopen_mock: object) -> None:
        urlopen_mock.return_value = FakeResponse({"executionId": "run-1", "status": "queued"})
        client = SwarmClawClient("http://hermes-swarmclaw:3456", "private-key")

        execution = client.create_execution(
            SwarmClawExecutionRequest(
                gateway_task_id="task-1",
                provider_connection_id="connection-1",
                organization_id="org-1",
                workspace_id="workspace-1",
                project_id=None,
                user_id="user-1",
                input="Подготовь отчёт",
                instructions="Работай только в выбранном workspace",
            )
        )

        self.assertEqual(execution.execution_id, "run-1")
        self.assertEqual(execution.status, "queued")
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(request.full_url, "http://hermes-swarmclaw:3456/api/internal/hermes/executions")
        self.assertEqual(request.get_header("X-hermes-service-key"), "private-key")
        self.assertEqual(json.loads(request.data.decode("utf-8"))["gatewayTaskId"], "task-1")
        self.assertEqual(
            json.loads(request.data.decode("utf-8"))["providerConnectionId"],
            "connection-1",
        )

    @patch("client.urlopen")
    def test_stop_execution_returns_execution_state(self, urlopen_mock: object) -> None:
        urlopen_mock.return_value = FakeResponse({"executionId": "run-1", "status": "stopping"})
        client = SwarmClawClient("http://hermes-swarmclaw:3456", "private-key")

        execution = client.stop_execution("run-1")

        self.assertEqual(execution.status, "stopping")
        request = urlopen_mock.call_args.args[0]
        self.assertEqual(request.full_url, "http://hermes-swarmclaw:3456/api/internal/hermes/executions/run-1/stop")
