import logging

logger = logging.getLogger(__name__)


def _on_session_start(**kwargs):
    logger.info("[Hermes Platform] Session started: %s", kwargs.get("session_id"))


def _on_session_end(**kwargs):
    logger.info("[Hermes Platform] Session ended: %s", kwargs.get("session_id"))


def register(ctx):
    logger.info("[Hermes Platform] Plugin loaded")

    ctx.register_hook("on_session_start", _on_session_start)
    ctx.register_hook("on_session_end", _on_session_end)
