"""Shared retry policy helpers for the synchronous and asynchronous clients."""

from __future__ import annotations

import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Callable, Optional


RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})


def parse_retry_after(value: Optional[str], now: Optional[datetime] = None) -> Optional[float]:
    """Parse a Retry-After value expressed as seconds or an HTTP date."""
    if not value:
        return None

    try:
        seconds = float(value)
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
        if retry_at.tzinfo is None:
            retry_at = retry_at.replace(tzinfo=timezone.utc)
        current = now or datetime.now(timezone.utc)
        return max(0.0, (retry_at - current).total_seconds())
    return max(0.0, seconds)


def is_retryable_status(status_code: int) -> bool:
    return status_code in RETRYABLE_STATUS_CODES


def retry_delay(
    attempt: int,
    retry_after: Optional[str] = None,
    *,
    now: Optional[datetime] = None,
    random_value: Optional[float] = None,
    base_delay: float = 0.5,
    max_delay: float = 30.0,
) -> float:
    """Return a bounded Retry-After delay or exponential full-jitter delay."""
    server_delay = parse_retry_after(retry_after, now=now)
    if server_delay is not None:
        return min(server_delay, max_delay)

    upper_bound = min(max_delay, base_delay * (2**attempt))
    return (random_value if random_value is not None else random.random()) * upper_bound


def should_retry(attempt: int, max_retries: int, status_code: Optional[int] = None) -> bool:
    return attempt < max_retries and (status_code is None or is_retryable_status(status_code))
