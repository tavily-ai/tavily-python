"""
Custom exception classes for the Tavily API client.

This module defines custom exception classes that are raised when specific error
conditions are encountered while interacting with the Tavily API. These exceptions
provide more specific error handling capabilities than generic exceptions.

The exceptions include:
- UsageLimitExceededError: Raised when API usage limits are exceeded
- BadRequestError: Raised for malformed or invalid requests
- ForbiddenError: Raised when access is forbidden
- InvalidAPIKeyError: Raised when an invalid API key is provided
- MissingAPIKeyError: Raised when no API key is provided
"""


class UsageLimitExceededError(Exception):
    """Exception raised when the API usage limit is exceeded.

    This exception is raised when a request would exceed the allowed usage limits
    of the Tavily API, such as rate limits or quota limits.

    Args:
        message (str): A detailed error message explaining the limit exceeded.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a detailed error message.

        Args:
            message (str): A detailed error message explaining the limit exceeded.
        """
        super().__init__(message)


class BadRequestError(Exception):
    """Exception raised for malformed or invalid API requests.

    This exception is raised when a request to the Tavily API is malformed or
    contains invalid parameters.

    Args:
        message (str): A detailed error message explaining the request error.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a detailed error message.

        Args:
            message (str): A detailed error message explaining the request error.
        """
        super().__init__(message)


class ForbiddenError(Exception):
    """Exception raised when access to the API is forbidden.

    This exception is raised when a request is forbidden by the Tavily API,
    typically due to insufficient permissions or access restrictions.

    Args:
        message (str): A detailed error message explaining the access restriction.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a detailed error message.

        Args:
            message (str): A detailed error message explaining the access restriction.
        """
        super().__init__(message)


class InvalidAPIKeyError(Exception):
    """Exception raised when an invalid API key is provided.

    This exception is raised when the provided API key is invalid or has been
    revoked by the Tavily API.

    Args:
        message (str): A detailed error message explaining the API key issue.
    """

    def __init__(self, message: str) -> None:
        """Initialize the exception with a detailed error message.

        Args:
            message (str): A detailed error message explaining the API key issue.
        """
        super().__init__(message)


class MissingAPIKeyError(Exception):
    """Exception raised when no API key is provided.

    This exception is raised when no API key is provided either through the
    constructor or environment variables.

    Note:
        The API key can be provided either through the TavilyClient constructor
        or by setting the TAVILY_API_KEY environment variable.
    """

    def __init__(self) -> None:
        """Initialize the exception with a standard error message."""
        super().__init__(
            "No API key provided. Please provide the api_key attribute or set the TAVILY_API_KEY environment variable."
        )
