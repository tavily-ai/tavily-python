from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Mapping, Optional


def parse_retry_after(headers):
    """Parse an HTTP ``Retry-After`` header value into seconds.

    Handles both forms defined by RFC 7231 §7.1.3:

    - a non-negative decimal integer of seconds, e.g. ``"120"``
    - an HTTP-date, e.g. ``"Wed, 21 Oct 2015 07:28:00 GMT"``

    Returns ``None`` when the header is absent or cannot be parsed.
    Accepts any mapping-like headers object (``requests`` / ``httpx``).
    """
    if not headers:
        return None
    raw = headers.get("Retry-After") or headers.get("retry-after")
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None
    try:
        return float(raw)
    except ValueError:
        pass
    try:
        when = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        return None
    if when is None:
        return None
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)
    delta = (when - datetime.now(timezone.utc)).total_seconds()
    return max(delta, 0.0)


class UsageLimitExceededError(Exception):
    """Raised on HTTP 429 responses from the Tavily API.

    ``retry_after`` carries the server-recommended wait (seconds) parsed from
    the ``Retry-After`` response header when present, so callers can honor the
    server's backoff instead of guessing. ``None`` when the header is absent
    or unparseable.
    """

    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class BadRequestError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ForbiddenError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class InvalidAPIKeyError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class TimeoutError(Exception):
    def __init__(self, timeout: float):
        super().__init__(f"Request timed out after {timeout} seconds.")


class MissingAPIKeyError(Exception):
    def __init__(self):
        super().__init__(
            "No API key provided. Please provide the api_key attribute or set the TAVILY_API_KEY environment variable."
        )
