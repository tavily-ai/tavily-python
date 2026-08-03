from datetime import datetime, timezone

from tavily.retry import is_retryable_status, parse_retry_after, retry_delay, should_retry


def test_parse_retry_after_seconds_and_invalid_values():
    assert parse_retry_after("3") == 3
    assert parse_retry_after("invalid") is None
    assert parse_retry_after(None) is None


def test_parse_retry_after_http_date():
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert parse_retry_after("Thu, 01 Jan 2026 00:00:03 GMT", now=now) == 3


def test_retry_delay_prefers_server_value_and_caps_it():
    assert retry_delay(0, "45", max_delay=30) == 30
    assert retry_delay(2, random_value=0.5, base_delay=1) == 2


def test_retry_policy_limits_attempts_and_statuses():
    assert is_retryable_status(429)
    assert is_retryable_status(503)
    assert not is_retryable_status(400)
    assert should_retry(0, 1, 429)
    assert not should_retry(1, 1, 429)
    assert not should_retry(0, 1, 400)
