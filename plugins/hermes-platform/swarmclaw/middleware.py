from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def llm_request(**kwargs):
    logger.info("[SwarmClaw] LLM request intercepted")
    return None


def tool_request(**kwargs):
    logger.info("[SwarmClaw] Tool request intercepted")
    return None


def register_middleware(ctx):
    logger.info("[SwarmClaw] Registering middleware")

    ctx.register_middleware(
        "llm_request",
        llm_request,
    )

    ctx.register_middleware(
        "tool_request",
        tool_request,
    )
