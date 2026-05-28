from typing import Any, List, Optional


class UsageLimitExceededError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


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
