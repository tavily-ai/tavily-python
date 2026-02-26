"""Tests for custom session functionality."""

import pytest
import requests
from tavily import TavilyClient


def test_custom_session_basic():
    """Test that a custom session is properly used."""
    # Create a custom session with a custom header
    custom_session = requests.Session()
    custom_session.headers.update({"X-Custom-Header": "test-value"})

    # Initialize client with custom session
    client = TavilyClient(api_key="test-key", session=custom_session)

    # Verify the session is the one we passed
    assert client.session is custom_session

    # Verify our custom header is still there
    assert "X-Custom-Header" in client.session.headers
    assert client.session.headers["X-Custom-Header"] == "test-value"

    # Verify Tavily headers were added
    assert "Authorization" in client.session.headers
    assert client.session.headers["Authorization"] == "Bearer test-key"
    assert client.session.headers["Content-Type"] == "application/json"

    client.close()


def test_custom_session_with_proxies():
    """Test that proxies are properly applied to custom session."""
    custom_session = requests.Session()

    proxies = {
        "http": "http://proxy.example.com:8080",
        "https": "https://proxy.example.com:8080",
    }

    client = TavilyClient(api_key="test-key", proxies=proxies, session=custom_session)

    # Verify proxies were applied to the custom session
    assert client.session.proxies.get("http") == "http://proxy.example.com:8080"
    assert client.session.proxies.get("https") == "https://proxy.example.com:8080"

    client.close()


def test_custom_session_with_azure_apim_headers():
    """Test custom session with Azure APIM style authentication."""
    custom_session = requests.Session()
    custom_session.headers.update(
        {
            "Ocp-Apim-Subscription-Key": "apim-subscription-key-123",
            "X-Tenant-ID": "tenant-456",
        }
    )

    client = TavilyClient(
        api_key="dummy-key",
        api_base_url="https://apim.example.com/tavily",
        session=custom_session,
    )

    # Verify custom APIM headers are preserved
    assert (
        client.session.headers["Ocp-Apim-Subscription-Key"]
        == "apim-subscription-key-123"
    )
    assert client.session.headers["X-Tenant-ID"] == "tenant-456"

    # Verify base URL is set correctly
    assert client.base_url == "https://apim.example.com/tavily"

    client.close()


def test_default_session_when_none_provided():
    """Test that default session is created when none is provided."""
    client = TavilyClient(api_key="test-key")

    # Verify a session was created
    assert client.session is not None
    assert isinstance(client.session, requests.Session)

    # Verify headers were set
    assert client.session.headers["Authorization"] == "Bearer test-key"

    client.close()


def test_custom_session_with_context_manager():
    """Test that custom session works with context manager."""
    custom_session = requests.Session()
    custom_session.headers.update({"X-Custom": "value"})

    with TavilyClient(api_key="test-key", session=custom_session) as client:
        assert client.session is custom_session
        assert "X-Custom" in client.session.headers

    # Session should be closed after context manager exits
    # Note: The custom session is closed by the context manager


def test_custom_session_preserves_existing_auth():
    """Test that custom session auth is preserved (not overridden)."""
    custom_session = requests.Session()
    # Set a custom authorization that should be PRESERVED
    custom_session.headers.update({"Authorization": "Bearer custom-token"})

    client = TavilyClient(api_key="new-api-key", session=custom_session)

    # The client should PRESERVE the custom Authorization header
    # This allows enterprise API gateways to use custom auth (e.g., Azure AD JWT)
    assert client.session.headers["Authorization"] == "Bearer custom-token"

    client.close()
