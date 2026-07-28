from __future__ import annotations

import logging

from .swarmclaw import register_middleware
from .cli import register_cli

logger = logging.getLogger(__name__)


def _on_session_start(**kwargs):
    logger.info("[Hermes Platform] Session started: %s", kwargs.get("session_id"))


def _on_session_end(**kwargs):
    logger.info("[Hermes Platform] Session ended: %s", kwargs.get("session_id"))


def register(ctx):
    logger.info("[Hermes Platform] Plugin loaded")

    #
    # Hooks
    #
    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("on_session_end", _on_session_end)

    #
    # Commands
    #
    ctx.register_cli_command(
        name="platform",
        help="Hermes Platform management",
        setup_fn=register_cli,
        description="Manage Hermes Platform infrastructure",
    )

    #
    # Middleware
    #
    register_middleware(ctx)

    logger.info("[Hermes Platform] SwarmClaw middleware registered")
