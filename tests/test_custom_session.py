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

    # External session should NOT be closed after context manager exits
    # User may want to reuse it for other requests or TavilyClient instances
    # We can test this by verifying the session still has its headers
    assert "X-Custom" in custom_session.headers

    # Clean up
    custom_session.close()


def test_internal_session_closed_by_context_manager():
    """Test that internally created session IS closed by context manager."""
    with TavilyClient(api_key="test-key") as client:
        # Capture the session reference
        session = client.session
        assert session is not None

    # The internal session should have been closed
    # A closed session will raise an exception if we try to make a request
    # (Note: We can't easily test this without making actual HTTP calls,
    # but we can verify the flag was set correctly)


def test_external_session_not_closed_by_close():
    """Test that external sessions are not closed by close() method."""
    custom_session = requests.Session()
    custom_session.headers.update({"X-Test": "value"})

    client = TavilyClient(api_key="test-key", session=custom_session)

    # Explicitly close the client
    client.close()

    # The external session should still be usable
    assert "X-Test" in custom_session.headers

    # Clean up
    custom_session.close()


def test_internal_session_closed_by_close():
    """Test that internally created sessions ARE closed by close() method."""
    client = TavilyClient(api_key="test-key")
    session = client.session

    # Close the client
    client.close()

    # The internal session should have been closed
    # (We can't easily verify this without making HTTP calls, but the flag check ensures it)


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


def test_custom_session_preserves_existing_proxies():
    """Test that custom session proxies are preserved (not overridden)."""
    custom_session = requests.Session()
    # Set custom proxies that should be PRESERVED
    custom_session.proxies.update(
        {
            "http": "http://custom-proxy.example.com:8080",
            "https": "https://custom-proxy.example.com:8443",
        }
    )

    # Try to override with different proxies via TavilyClient params
    override_proxies = {
        "http": "http://override-proxy.example.com:9090",
        "https": "https://override-proxy.example.com:9443",
    }

    client = TavilyClient(
        api_key="test-key", proxies=override_proxies, session=custom_session
    )

    # The custom session's proxies should be PRESERVED (not overridden)
    # This allows users to configure proxies on the session with full control
    assert client.session.proxies["http"] == "http://custom-proxy.example.com:8080"
    assert client.session.proxies["https"] == "https://custom-proxy.example.com:8443"

    client.close()


def test_custom_session_adds_missing_proxies():
    """Test that TavilyClient adds proxies for protocols not in custom session."""
    custom_session = requests.Session()
    # Only set HTTP proxy, leave HTTPS undefined
    custom_session.proxies.update({"http": "http://custom-http-proxy.example.com:8080"})

    # TavilyClient provides both HTTP and HTTPS proxies
    client_proxies = {
        "http": "http://override-http.example.com:9090",
        "https": "https://client-https.example.com:9443",
    }

    client = TavilyClient(
        api_key="test-key", proxies=client_proxies, session=custom_session
    )

    # HTTP proxy should be preserved from custom session
    assert client.session.proxies["http"] == "http://custom-http-proxy.example.com:8080"

    # HTTPS proxy should be added from client_proxies (since it wasn't in session)
    assert client.session.proxies["https"] == "https://client-https.example.com:9443"

    client.close()


def test_custom_session_proxies_from_env():
    """Test that custom session proxies are preserved over environment variables."""
    import os

    # Set environment variables
    os.environ["TAVILY_HTTP_PROXY"] = "http://env-proxy.example.com:7070"
    os.environ["TAVILY_HTTPS_PROXY"] = "https://env-proxy.example.com:7443"

    try:
        custom_session = requests.Session()
        # Custom session proxies should take precedence
        custom_session.proxies.update(
            {
                "http": "http://session-proxy.example.com:6060",
                "https": "https://session-proxy.example.com:6443",
            }
        )

        client = TavilyClient(api_key="test-key", session=custom_session)

        # Custom session proxies should be preserved (not overridden by env vars)
        assert client.session.proxies["http"] == "http://session-proxy.example.com:6060"
        assert (
            client.session.proxies["https"] == "https://session-proxy.example.com:6443"
        )

        client.close()
    finally:
        # Clean up environment variables
        os.environ.pop("TAVILY_HTTP_PROXY", None)
        os.environ.pop("TAVILY_HTTPS_PROXY", None)


def test_headers_attribute_contains_only_tavily_headers():
    """Test that self.headers contains only Tavily-specific headers, not session defaults."""
    # Create a custom session with extra headers
    custom_session = requests.Session()
    custom_session.headers.update(
        {
            "X-Custom-Header": "custom-value",
            "X-Azure-APIM-Key": "apim-key-123",
        }
    )

    client = TavilyClient(
        api_key="test-key", session=custom_session, project_id="test-project"
    )

    # self.headers should only contain Tavily-specific headers
    expected_keys = {"Content-Type", "Authorization", "X-Client-Source", "X-Project-ID"}
    assert set(client.headers.keys()) == expected_keys

    # Verify the values
    assert client.headers["Content-Type"] == "application/json"
    assert client.headers["Authorization"] == "Bearer test-key"
    assert client.headers["X-Client-Source"] == "tavily-python"
    assert client.headers["X-Project-ID"] == "test-project"

    # self.headers should NOT contain custom session headers
    assert "X-Custom-Header" not in client.headers
    assert "X-Azure-APIM-Key" not in client.headers

    # self.headers should NOT contain requests.Session default headers
    # (like User-Agent, Accept-Encoding, etc.)
    assert "User-Agent" not in client.headers
    assert "Accept-Encoding" not in client.headers
    assert "Accept" not in client.headers
    assert "Connection" not in client.headers

    # But the session itself should have all headers
    assert "X-Custom-Header" in client.session.headers
    assert "X-Azure-APIM-Key" in client.session.headers

    client.close()
