import pytest
import os
import asyncio

import tavily.tavily as sync_tavily
import tavily.async_tavily as async_tavily
from tavily.errors import InvalidAPIKeyError

@pytest.fixture
def set_api_key():
    old_key = os.getenv("TAVILY_API_KEY")
    os.environ["TAVILY_API_KEY"] = "test_api_key"
    yield
    if old_key is not None:
        os.environ["TAVILY_API_KEY"] = old_key
    elif "TAVILY_API_KEY" in os.environ:
        del os.environ["TAVILY_API_KEY"]

@pytest.fixture
def clear_api_key():
    old_key = os.getenv("TAVILY_API_KEY")
    if old_key:
        del os.environ["TAVILY_API_KEY"]
    yield
    if old_key:
        os.environ["TAVILY_API_KEY"] = old_key

def test_load_key_from_env(set_api_key):
    sync_tavily.TavilyClient()
    async_tavily.AsyncTavilyClient()

    # No error should be raised

def test_no_api_key_creates_keyless_client(clear_api_key):
    """With no API key (None or empty string) the client constructs in keyless mode."""
    for ctor_args in [{"api_key": ""}, {}, {"api_key": None}]:
        sync_client = sync_tavily.TavilyClient(**ctor_args)
        assert sync_client._keyless is True
        assert "Authorization" not in sync_client.headers
        assert sync_client.headers.get("X-Tavily-Access-Mode") == "keyless"
        assert sync_client.headers.get("X-Client-Source") == "tavily-python-keyless"

        async_client = async_tavily.AsyncTavilyClient(**ctor_args)
        assert async_client._keyless is True

def test_invalid_api_key():
    with pytest.raises(InvalidAPIKeyError):
        sync_tavily.TavilyClient(api_key="invalid_api_key").search("What is Tavily?")

    with pytest.raises(InvalidAPIKeyError):
        print(async_tavily.httpx.AsyncClient.post)
        print(asyncio.run(async_tavily.AsyncTavilyClient(api_key="invalid_api_key").search("What is Tavily?")))
