"""Tests for the opt-in automatic retry behavior (max_retries).

Covers Retry-After parsing, the default-off behavior, retry on 429/5xx for
idempotent endpoints, connection-error retries, and the 429-only policy for
job-creating endpoints (crawl, research).
"""
import asyncio
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

import httpx
import pytest
import requests

from tavily.tavily import TavilyClient
from tavily.async_tavily import AsyncTavilyClient
from tavily.errors import BadRequestError, UsageLimitExceededError
from tavily.utils import parse_retry_after, retry_delay


# ---------------------------------------------------------------------------
# Retry-After helpers
# ---------------------------------------------------------------------------

def test_parse_retry_after_seconds():
    assert parse_retry_after({"Retry-After": "7"}) == pytest.approx(7.0)


def test_parse_retry_after_http_date():
    future = datetime.now(timezone.utc) + timedelta(seconds=30)
    value = parse_retry_after({"Retry-After": format_datetime(future)})
    assert value is not None
    assert 0 < value <= 30


def test_parse_retry_after_missing_or_garbage():
    assert parse_retry_after(None) is None
    assert parse_retry_after({}) is None
    assert parse_retry_after({"Retry-After": "not-a-date"}) is None


def test_retry_delay_honors_retry_after():
    assert retry_delay(1, {"Retry-After": "3"}) == pytest.approx(3.0)


def test_retry_delay_backoff_bounds():
    for attempt, cap in ((1, 1.0), (2, 2.0), (3, 4.0)):
        delay = retry_delay(attempt)
        assert 0 <= delay <= cap


# ---------------------------------------------------------------------------
# Sync client stubs
# ---------------------------------------------------------------------------

class FakeResponse:
    def __init__(self, status_code, body=None, headers=None):
        self.status_code = status_code
        self._body = body if body is not None else {}
        self.headers = headers or {}

    def json(self):
        return self._body

    def raise_for_status(self):
        raise requests.HTTPError(f"{self.status_code} error")


class FakeSession:
    """A requests.Session stand-in that plays back a scripted sequence."""

    def __init__(self, script):
        self.headers = {}
        self.proxies = {}
        self._script = list(script)
        self.calls = []

    def _next(self, method, url):
        self.calls.append((method, url))
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    def post(self, url, data=None, timeout=None, headers=None, stream=False):
        return self._next("POST", url)

    def get(self, url, params=None, **kwargs):
        return self._next("GET", url)

    def close(self):
        pass


RATE_LIMIT_BODY = {"detail": {"error": "rate limited"}}
OK_SEARCH = {"query": "q", "results": [], "response_time": 0.1}


@pytest.fixture
def record_sync_sleeps(monkeypatch):
    delays = []

    def recorder(self, attempt, response=None):
        delays.append(retry_delay(attempt, response.headers if response is not None else None))

    monkeypatch.setattr(TavilyClient, "_sleep_before_retry", recorder)
    return delays


def make_sync_client(script, **kwargs):
    session = FakeSession(script)
    client = TavilyClient(api_key="tvly-test", session=session, **kwargs)
    return client, session


def test_sync_no_retry_by_default(record_sync_sleeps):
    client, session = make_sync_client([FakeResponse(429, RATE_LIMIT_BODY), FakeResponse(200, OK_SEARCH)])
    with pytest.raises(UsageLimitExceededError):
        client.search("q")
    assert len(session.calls) == 1
    assert record_sync_sleeps == []


def test_sync_search_retries_on_429_and_honors_retry_after(record_sync_sleeps):
    client, session = make_sync_client(
        [FakeResponse(429, RATE_LIMIT_BODY, {"Retry-After": "7"}), FakeResponse(200, OK_SEARCH)],
        max_retries=2,
    )
    result = client.search("q")
    assert result == OK_SEARCH
    assert len(session.calls) == 2
    assert record_sync_sleeps == [7.0]


def test_sync_search_exhausts_retries(record_sync_sleeps):
    client, session = make_sync_client(
        [FakeResponse(429, RATE_LIMIT_BODY)] * 3,
        max_retries=2,
    )
    with pytest.raises(UsageLimitExceededError):
        client.search("q")
    assert len(session.calls) == 3


def test_sync_search_never_retries_400(record_sync_sleeps):
    client, session = make_sync_client(
        [FakeResponse(400, {"detail": {"error": "bad request"}}), FakeResponse(200, OK_SEARCH)],
        max_retries=2,
    )
    with pytest.raises(BadRequestError):
        client.search("q")
    assert len(session.calls) == 1


def test_sync_extract_retries_on_503(record_sync_sleeps):
    ok = {"results": [], "failed_results": [], "response_time": 0.1}
    client, session = make_sync_client([FakeResponse(503), FakeResponse(200, ok)], max_retries=1)
    result = client.extract(urls=["https://example.com"])
    assert result == ok
    assert len(session.calls) == 2


def test_sync_search_retries_connection_error(record_sync_sleeps):
    client, session = make_sync_client(
        [requests.exceptions.ConnectionError("boom"), FakeResponse(200, OK_SEARCH)],
        max_retries=1,
    )
    result = client.search("q")
    assert result == OK_SEARCH
    assert len(session.calls) == 2


def test_sync_crawl_does_not_retry_503(record_sync_sleeps):
    client, session = make_sync_client(
        [FakeResponse(503), FakeResponse(200, {"results": []})],
        max_retries=2,
    )
    with pytest.raises(requests.HTTPError):
        client.crawl("https://example.com")
    assert len(session.calls) == 1


def test_sync_crawl_retries_429(record_sync_sleeps):
    ok = {"base_url": "https://example.com", "results": [], "response_time": 0.1}
    client, session = make_sync_client(
        [FakeResponse(429, RATE_LIMIT_BODY), FakeResponse(200, ok)],
        max_retries=1,
    )
    result = client.crawl("https://example.com")
    assert result == ok
    assert len(session.calls) == 2


def test_sync_research_does_not_retry_503(record_sync_sleeps):
    client, session = make_sync_client(
        [FakeResponse(503), FakeResponse(200, {"request_id": "r1"})],
        max_retries=2,
    )
    with pytest.raises(requests.HTTPError):
        client.research("topic")
    assert len(session.calls) == 1


def test_sync_get_research_retries_on_503(record_sync_sleeps):
    ok = {"request_id": "r1", "status": "completed", "content": "done"}
    client, session = make_sync_client([FakeResponse(503), FakeResponse(200, ok)], max_retries=1)
    result = client.get_research("r1")
    assert result == ok
    assert len(session.calls) == 2


# ---------------------------------------------------------------------------
# Async client stubs
# ---------------------------------------------------------------------------

class FakeAsyncResponse:
    def __init__(self, status_code, body=None, headers=None):
        self.status_code = status_code
        self._body = body if body is not None else {}
        self.headers = headers or {}

    def json(self):
        return self._body

    def raise_for_status(self):
        raise RuntimeError(f"{self.status_code} error")


class FakeAsyncClient:
    """An httpx.AsyncClient stand-in that plays back a scripted sequence."""

    def __init__(self, script):
        self.headers = {}
        self.base_url = ""
        self._script = list(script)
        self.calls = []

    def _next(self, method, url):
        self.calls.append((method, url))
        item = self._script.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    async def post(self, url, content=None, timeout=None, headers=None):
        return self._next("POST", url)

    async def get(self, url, timeout=None, headers=None, params=None):
        return self._next("GET", url)


@pytest.fixture
def record_async_sleeps(monkeypatch):
    delays = []

    async def recorder(self, attempt, response=None):
        delays.append(retry_delay(attempt, response.headers if response is not None else None))

    monkeypatch.setattr(AsyncTavilyClient, "_sleep_before_retry", recorder)
    return delays


def make_async_client(script, **kwargs):
    fake = FakeAsyncClient(script)
    client = AsyncTavilyClient(api_key="tvly-test", client=fake, **kwargs)
    return client, fake


def test_async_no_retry_by_default(record_async_sleeps):
    client, fake = make_async_client([FakeAsyncResponse(429, RATE_LIMIT_BODY), FakeAsyncResponse(200, OK_SEARCH)])
    with pytest.raises(UsageLimitExceededError):
        asyncio.run(client.search("q"))
    assert len(fake.calls) == 1
    assert record_async_sleeps == []


def test_async_search_retries_on_429_and_honors_retry_after(record_async_sleeps):
    client, fake = make_async_client(
        [FakeAsyncResponse(429, RATE_LIMIT_BODY, {"Retry-After": "3"}), FakeAsyncResponse(200, OK_SEARCH)],
        max_retries=2,
    )
    result = asyncio.run(client.search("q"))
    assert result == OK_SEARCH
    assert len(fake.calls) == 2
    assert record_async_sleeps == [3.0]


def test_async_search_retries_connect_error(record_async_sleeps):
    request = httpx.Request("POST", "https://api.tavily.com/search")
    client, fake = make_async_client(
        [httpx.ConnectError("boom", request=request), FakeAsyncResponse(200, OK_SEARCH)],
        max_retries=1,
    )
    result = asyncio.run(client.search("q"))
    assert result == OK_SEARCH
    assert len(fake.calls) == 2


def test_async_crawl_does_not_retry_503(record_async_sleeps):
    client, fake = make_async_client(
        [FakeAsyncResponse(503), FakeAsyncResponse(200, {"results": []})],
        max_retries=2,
    )
    with pytest.raises(RuntimeError):
        asyncio.run(client.crawl("https://example.com"))
    assert len(fake.calls) == 1
