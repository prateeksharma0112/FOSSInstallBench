"""Compact logging for OpenHands LLM retries."""

import logging
from collections.abc import Callable

import structlog

from installbench.models.execution import RunPhase

logger = structlog.get_logger(__name__)

# OpenHands includes the complete provider response in every retry log.
logging.getLogger("openhands.sdk.llm.utils.retry_mixin").setLevel(logging.CRITICAL + 1)


def create_retry_listener(
    phase: RunPhase,
) -> Callable[[int, int, BaseException | None], None]:
    """Create a concise retry logger for one agent phase."""

    def log_retry(
        attempt_number: int,
        _num_retries: int,
        error: BaseException | None,
    ) -> None:
        logger.warning(
            "llm_request_retry",
            phase=phase,
            attempt=attempt_number,
            error_type=type(error).__name__ if error else "unknown",
        )

    return log_retry
