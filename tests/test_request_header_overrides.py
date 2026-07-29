"""Per-request header overrides (ENG-747).

Endpoint methods accept ``project_id``, ``session_id``, ``human_id``, and
``client_name`` as per-call kwargs. Each is sent as a request-level header on
that call only: it wins over the client-level default, never leaks into the
JSON body, and never persists onto the session for later calls.
"""

import asyncio

import pytest

import tavily.tavily as sync_tavily
import tavily.async_tavily as async_tavily

OVERRIDE_HEADERS = [
    ("project_id", "X-Project-ID"),
    ("session_id", "X-Session-Id"),
    ("human_id", "X-Human-Id"),
    ("client_name", "X-Client-Name"),
]

# (method name, positional args) for every endpoint that supports overrides.
ENDPOINT_CALLS = [
    ("search", ("What is Tavily?",)),
    ("extract", ("https://tavily.com",)),
    ("crawl", ("https://tavily.com",)),
    ("map", ("https://tavily.com",)),
    ("research", ("What is Tavily?",)),
]

DUMMY_BODY = {"query": "ok", "results": [], "response_time": 0.1}


def run(coro):
    return asyncio.new_event_loop().run_until_complete(coro)


def get_header(request, name):
    """Case-insensitive header lookup: requests preserves case, httpx lowercases."""
    lowered = {k.lower(): v for k, v in request.headers.items()}
    return lowered.get(name.lower())


@pytest.mark.parametrize("kwarg,header", OVERRIDE_HEADERS)
def test_sync_search_override_sets_request_header(sync_interceptor, sync_client, kwarg, header):
    sync_interceptor.set_response(200, json=DUMMY_BODY)
    sync_client.search("What is Tavily?", **{kwarg: "per-request-value"})
    assert get_header(sync_interceptor.get_request(), header) == "per-request-value"


@pytest.mark.parametrize("kwarg,header", OVERRIDE_HEADERS)
def test_async_search_override_sets_request_header(async_interceptor, async_client, kwarg, header):
    async_interceptor.set_response(200, json=DUMMY_BODY)
    run(async_client.search("What is Tavily?", **{kwarg: "per-request-value"}))
    assert get_header(async_interceptor.get_request(), header) == "per-request-value"


@pytest.mark.parametrize("method,args", ENDPOINT_CALLS)
def test_sync_project_id_sent_on_every_endpoint(sync_interceptor, sync_client, method, args):
    sync_interceptor.set_response(200, json=DUMMY_BODY)
    getattr(sync_client, method)(*args, project_id="proj-per-call")
    assert get_header(sync_interceptor.get_request(), "X-Project-ID") == "proj-per-call"


@pytest.mark.parametrize("method,args", ENDPOINT_CALLS)
def test_async_project_id_sent_on_every_endpoint(async_interceptor, async_client, method, args):
    async_interceptor.set_response(200, json=DUMMY_BODY)
    run(getattr(async_client, method)(*args, project_id="proj-per-call"))
    assert get_header(async_interceptor.get_request(), "X-Project-ID") == "proj-per-call"


def test_sync_per_request_project_id_overrides_client_default(sync_interceptor):
    client = sync_tavily.TavilyClient(api_key="tvly-test", project_id="proj-default")
    sync_interceptor.set_response(200, json=DUMMY_BODY)
    client.search("What is Tavily?", project_id="proj-override")
    assert get_header(sync_interceptor.get_request(), "X-Project-ID") == "proj-override"


def test_async_per_request_project_id_overrides_client_default(async_interceptor):
    client = async_tavily.AsyncTavilyClient(api_key="tvly-test", project_id="proj-default")
    async_interceptor.set_response(200, json=DUMMY_BODY)
    run(client.search("What is Tavily?", project_id="proj-override"))
    assert get_header(async_interceptor.get_request(), "X-Project-ID") == "proj-override"


def test_sync_project_id_kwarg_not_leaked_into_body(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=DUMMY_BODY)
    sync_client.search("What is Tavily?", project_id="proj-per-call")
    assert "project_id" not in sync_interceptor.get_request().json()


def test_async_project_id_kwarg_not_leaked_into_body(async_interceptor, async_client):
    async_interceptor.set_response(200, json=DUMMY_BODY)
    run(async_client.search("What is Tavily?", project_id="proj-per-call"))
    assert "project_id" not in async_interceptor.get_request().json()


def test_sync_project_id_override_does_not_persist_across_calls(sync_interceptor):
    client = sync_tavily.TavilyClient(api_key="tvly-test", project_id="proj-default")
    sync_interceptor.set_response(200, json=DUMMY_BODY)
    client.search("What is Tavily?", project_id="proj-override")
    client.search("What is Tavily?")
    assert get_header(sync_interceptor.get_request(), "X-Project-ID") == "proj-default"


def test_async_project_id_override_does_not_persist_across_calls(async_interceptor):
    client = async_tavily.AsyncTavilyClient(api_key="tvly-test", project_id="proj-default")
    async_interceptor.set_response(200, json=DUMMY_BODY)

    async def two_calls():
        await client.search("What is Tavily?", project_id="proj-override")
        await client.search("What is Tavily?")

    run(two_calls())
    assert get_header(async_interceptor.get_request(), "X-Project-ID") == "proj-default"
