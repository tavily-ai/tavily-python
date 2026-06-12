from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Mapping, Optional, Any , List


def _find_header(headers: Mapping[str, str], name: str) -> Optional[str]:
    """Return the value of ``name`` from ``headers`` with case-insensitive lookup."""
    target = name.lower()
    for key, value in headers.items():
        if key.lower() == target:
            return value
    return None


def _parse_retry_after(headers: Optional[Mapping[str, str]]) -> Optional[float]:
    """Parse an HTTP ``Retry-After`` header value into seconds.

    Handles both forms defined by RFC 7231 §7.1.3:

    - a non-negative decimal integer of seconds, e.g. ``"120"``
    - an HTTP-date, e.g. ``"Wed, 21 Oct 2015 07:28:00 GMT"``

    Semantics follow ``urllib3.util.Retry.parse_retry_after``: integer
    seconds first, then HTTP-date. Negative or past values clamp to ``0.0``.
    Returns ``None`` when the header is absent or cannot be parsed (including
    non-integer numerics, ``NaN``/``inf``, and malformed dates).

    Accepts any mapping-like ``headers`` object. Case-insensitive header name
    lookup is done explicitly so callers passing a plain ``dict`` (not only
    ``requests``/``httpx`` header containers) work correctly.
    """
    if not headers:
        return None
    raw = _find_header(headers, "Retry-After")
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None
    try:
        return max(float(int(raw)), 0.0)
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


class TavilyKeylessLimitError(UsageLimitExceededError):
    """Raised when a keyless request is rejected by the Tavily API."""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        window: Optional[str] = None,
        retry_after_seconds: Optional[int] = None,
        next_actions: Optional[List[Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.window = window
        self.retry_after_seconds = retry_after_seconds
        self.next_actions = next_actions or []

    def __str__(self) -> str:
        return self.message or ""


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


class KeylessUnsupportedEndpointError(Exception):
    """Raised when a method is called without an API key but does not support keyless mode.

    Only ``search`` and ``extract`` support keyless mode. Calling other methods
    keyless raises this error before any network request is sent.
    """

    def __init__(self, method: str):
        super().__init__(
            f"`{method}` is not available in keyless mode. "
            "Only `search` and `extract` can be called without an API key. "
            "Pass an `api_key` to TavilyClient (or set TAVILY_API_KEY) to use this method."
        )
        self.method = method
