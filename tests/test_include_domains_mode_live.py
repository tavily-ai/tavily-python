"""
Live tests for the `include_domains_mode` search param (boosted domains).

These hit the real Tavily API (no mocking) to confirm the param is accepted
end-to-end. Skipped unless a real TAVILY_API_KEY is set (CI uses the fake
"tvly-test" key, so this never runs there).
"""

import asyncio
import os
from urllib.parse import urlparse

import pytest

from tavily import TavilyClient, AsyncTavilyClient
from tavily.errors import BadRequestError

API_KEY = os.getenv("TAVILY_API_KEY")
requires_live_key = pytest.mark.skipif(
    not API_KEY or API_KEY == "tvly-test",
    reason="set a real TAVILY_API_KEY to run live tests",
)


@requires_live_key
def test_sync_search_with_include_domains_mode_boost_live():
    client = TavilyClient(api_key=API_KEY)
    response = client.search(
        "quarterly earnings outlook",
        include_domains=["bloomberg.com", "reuters.com"],
        include_domains_mode="boost",
    )
    assert isinstance(response.get("results"), list)
    assert len(response["results"]) > 0


@requires_live_key
def test_sync_search_with_include_domains_mode_filter_live():
    client = TavilyClient(api_key=API_KEY)
    response = client.search(
        "CEO background at Google",
        include_domains=["linkedin.com"],
        include_domains_mode="filter",
    )
    assert isinstance(response.get("results"), list)
    for result in response["results"]:
        host = urlparse(result["url"]).hostname or ""
        assert host == "linkedin.com" or host.endswith(".linkedin.com")


@requires_live_key
def test_sync_search_without_include_domains_mode_still_works_live():
    client = TavilyClient(api_key=API_KEY)
    response = client.search("What is the capital of France?")
    assert isinstance(response.get("results"), list)
    assert len(response["results"]) > 0


@requires_live_key
def test_async_search_with_include_domains_mode_boost_live():
    client = AsyncTavilyClient(api_key=API_KEY)
    response = asyncio.run(
        client.search(
            "quarterly earnings outlook",
            include_domains=["bloomberg.com", "reuters.com"],
            include_domains_mode="boost",
        )
    )
    assert isinstance(response.get("results"), list)
    assert len(response["results"]) > 0


@requires_live_key
def test_sync_search_include_domains_mode_without_include_domains_rejected_live():
    client = TavilyClient(api_key=API_KEY)
    with pytest.raises(BadRequestError):
        client.search("quarterly earnings outlook", include_domains_mode="boost")


@requires_live_key
def test_sync_search_include_domains_mode_boost_rejected_for_news_topic_live():
    client = TavilyClient(api_key=API_KEY)
    with pytest.raises(BadRequestError):
        client.search(
            "quarterly earnings outlook",
            topic="news",
            include_domains=["bloomberg.com"],
            include_domains_mode="boost",
        )


@requires_live_key
def test_sync_search_include_domains_mode_boost_rejected_for_fast_depth_live():
    client = TavilyClient(api_key=API_KEY)
    with pytest.raises(BadRequestError):
        client.search(
            "quarterly earnings outlook",
            search_depth="fast",
            include_domains=["bloomberg.com"],
            include_domains_mode="boost",
        )
