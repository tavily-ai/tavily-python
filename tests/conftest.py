import pytest
from tests.request_intercept import intercept_requests, clear_interceptor
import tavily.tavily as sync_tavily
import tavily.async_tavily as async_tavily

@pytest.fixture
def sync_interceptor():
    yield intercept_requests(sync_tavily)
    clear_interceptor(sync_tavily)

@pytest.fixture
def async_interceptor():
    yield intercept_requests(async_tavily)
    clear_interceptor(async_tavily)

@pytest.fixture
def sync_client():
    return sync_tavily.TavilyClient(api_key="tvly-test")

@pytest.fixture
def async_client():
    return async_tavily.AsyncTavilyClient(api_key="tvly-test")
