"""Tests for Retry-After header propagation on 429 responses.

Tavily API returns a ``Retry-After`` header when it rejects a request with
``429 Too Many Requests``. The SDK must expose that value on
``UsageLimitExceededError`` so callers can honor the server's recommended
wait instead of falling back to a fixed backoff.
"""

import asyncio

import pytest

from tavily.errors import UsageLimitExceededError


RATE_LIMIT_BODY = {"detail": {"error": "rate limit exceeded"}}


def test_sync_429_exposes_retry_after_seconds(sync_interceptor, sync_client):
    sync_interceptor.set_response(429, headers={"Retry-After": "7"}, json=RATE_LIMIT_BODY)

    with pytest.raises(UsageLimitExceededError) as exc_info:
        sync_client.search("What is Tavily?")

    assert exc_info.value.retry_after == pytest.approx(7.0)


def test_sync_429_retry_after_absent_is_none(sync_interceptor, sync_client):
    sync_interceptor.set_response(429, json=RATE_LIMIT_BODY)

    with pytest.raises(UsageLimitExceededError) as exc_info:
        sync_client.search("What is Tavily?")

    assert exc_info.value.retry_after is None


def test_sync_429_retry_after_http_date(sync_interceptor, sync_client):
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta

    future = datetime.now(timezone.utc) + timedelta(seconds=30)
    sync_interceptor.set_response(
        429,
        headers={"Retry-After": format_datetime(future, usegmt=True)},
        json=RATE_LIMIT_BODY,
    )

    with pytest.raises(UsageLimitExceededError) as exc_info:
        sync_client.search("What is Tavily?")

    assert exc_info.value.retry_after is not None
    assert 20 <= exc_info.value.retry_after <= 40


def test_sync_429_retry_after_malformed_is_none(sync_interceptor, sync_client):
    sync_interceptor.set_response(
        429, headers={"Retry-After": "not-a-number"}, json=RATE_LIMIT_BODY
    )

    with pytest.raises(UsageLimitExceededError) as exc_info:
        sync_client.search("What is Tavily?")

    assert exc_info.value.retry_after is None


def test_async_429_exposes_retry_after_seconds(async_interceptor, async_client):
    async_interceptor.set_response(429, headers={"Retry-After": "12"}, json=RATE_LIMIT_BODY)

    with pytest.raises(UsageLimitExceededError) as exc_info:
        asyncio.run(async_client.search("What is Tavily?"))

    assert exc_info.value.retry_after == pytest.approx(12.0)


def test_async_429_retry_after_absent_is_none(async_interceptor, async_client):
    async_interceptor.set_response(429, json=RATE_LIMIT_BODY)

    with pytest.raises(UsageLimitExceededError) as exc_info:
        asyncio.run(async_client.search("What is Tavily?"))

    assert exc_info.value.retry_after is None


def test_usage_limit_error_default_retry_after_is_none():
    err = UsageLimitExceededError("boom")
    assert err.retry_after is None


def test_usage_limit_error_accepts_retry_after():
    err = UsageLimitExceededError("boom", retry_after=3.5)
    assert err.retry_after == 3.5
