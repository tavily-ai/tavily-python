"""
Tavily API Client Package.

This package provides a Python client for interacting with the Tavily API, offering
both synchronous and asynchronous interfaces for web search, content extraction,
and more.

The package exports the following main components:

Classes:
    TavilyClient: The main synchronous client for the Tavily API
    AsyncTavilyClient: An asynchronous version of the Tavily client
    TavilyHybridClient: A client for hybrid RAG (Retrieval-Augmented Generation) operations
    Client: An alias for TavilyClient for backward compatibility

Exceptions:
    BadRequestError: Raised for malformed or invalid requests
    InvalidAPIKeyError: Raised when an invalid API key is provided
    MissingAPIKeyError: Raised when no API key is provided
    UsageLimitExceededError: Raised when API usage limits are exceeded

Example:
    >>> from tavily import TavilyClient
    >>> client = TavilyClient(api_key="your-api-key")
    >>> results = client.search("Python programming")
    >>> print(results)
"""

from .async_tavily import AsyncTavilyClient
from .errors import (
    BadRequestError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
    UsageLimitExceededError,
)
from .hybrid_rag import TavilyHybridClient
from .tavily import Client, TavilyClient


__all__ = [
    "AsyncTavilyClient",
    "BadRequestError",
    "Client",
    "TavilyClient",
    "TavilyHybridClient",
    "InvalidAPIKeyError",
    "MissingAPIKeyError",
    "UsageLimitExceededError",
]
