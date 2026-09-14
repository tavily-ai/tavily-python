import asyncio
import pytest

BASE_URL = "https://api.tavily.com"

dummy_queued_response = {
    "request_id": "test-request-123",
    "created_at": "2024-01-01T00:00:00Z",
    "status": "pending",
    "input": "Research the latest developments in AI",
    "model": "mini"
}

dummy_research_response = {
    "request_id": "test-request-123",
    "created_at": "2024-01-01T00:00:00Z",
    "completed_at": "2024-01-01T00:05:00Z",
    "status": "completed",
    "content": "This is a comprehensive research report on AI developments...",
    "sources": [
        {
            "title": "AI Research Paper",
            "url": "https://example.com/ai-paper",
        }
    ]
}

def validate_research_default(request, response):
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/research"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.json().get('input') == "Research the latest developments in AI"
    assert response == dummy_queued_response

def validate_research_specific(request, response):
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/research"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    
    request_json = request.json()
    for key, value in {
        "input": "Research the latest developments in AI",
        "model": "mini",
        "citation_format": "apa",
        "stream": True,
        "output_schema": {
            "title": "ResearchReport",
            "description": "A structured research report",
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}}
            }
        }
    }.items():
        assert request_json.get(key) == value

    assert response == dummy_queued_response

def validate_get_research(request, response):
    assert request.method == "GET"
    assert request.url == f"{BASE_URL}/research/test-request-123"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.params is None
    assert response == dummy_research_response

def test_sync_research_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_queued_response)
    response = sync_client.research("Research the latest developments in AI")
    request = sync_interceptor.get_request()
    validate_research_default(request, response)

def test_sync_research_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_queued_response)
    response = sync_client.research(
        input="Research the latest developments in AI",
        model="mini",
        citation_format="apa",
        stream=True,
        timeout=300,
        output_schema={
            "title": "ResearchReport",
            "description": "A structured research report",
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "key_points": {"type": "array", "items": {"type": "string"}}
            }
        }
    )

    request = sync_interceptor.get_request()
    # When stream=True, response is a generator
    assert hasattr(response, '__iter__') and not isinstance(response, (str, dict))
    validate_research_specific(request, dummy_queued_response)

def test_sync_get_research(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_research_response)
    response = sync_client.get_research("test-request-123")
    request = sync_interceptor.get_request()
    validate_get_research(request, response)

def test_async_research_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_queued_response)
    response = asyncio.run(async_client.research("Research the latest developments in AI"))
    request = async_interceptor.get_request()
    validate_research_default(request, response)

def test_async_research_specific(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_queued_response)
    
    async def run_test():
        response = await async_client.research(
            input="Research the latest developments in AI",
            model="mini",
            citation_format="apa",
            stream=True,
            timeout=300,
            output_schema={
                "title": "ResearchReport",
                "description": "A structured research report",
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "key_points": {"type": "array", "items": {"type": "string"}}
                }
            }
        )
        # When stream=True, response is an async generator
        assert hasattr(response, '__aiter__')
        try:
            async for chunk in response:
                # Just consume one chunk to trigger the request
                break
        except StopAsyncIteration:
            pass
        return response
    
    response = asyncio.run(run_test())
    request = async_interceptor.get_request()
    validate_research_specific(request, dummy_queued_response)

def test_async_get_research(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_research_response)
    response = asyncio.run(async_client.get_research("test-request-123"))
    request = async_interceptor.get_request()
    validate_get_research(request, response)


@pytest.mark.parametrize("flag,params", [(None, None), (False, {"include_usage": "false"}), (True, {"include_usage": "true"})])
def test_sync_get_research_usage(sync_interceptor, sync_client, flag, params):
    payload = {**dummy_research_response, "usage": {"credits": 1.25, "extra": "kept"}}
    sync_interceptor.set_response(200, json=payload)
    assert sync_client.get_research("test-request-123", include_usage=flag) == payload
    assert sync_interceptor.get_request().params == params


@pytest.mark.parametrize("flag,params", [(None, None), (False, {"include_usage": "false"}), (True, {"include_usage": "true"})])
def test_async_get_research_usage(async_interceptor, async_client, flag, params):
    payload = {**dummy_research_response, "usage": {"credits": 1.25, "extra": "kept"}}
    async_interceptor.set_response(200, json=payload)
    assert asyncio.run(async_client.get_research("test-request-123", include_usage=flag)) == payload
    assert async_interceptor.get_request().params == params


@pytest.mark.parametrize("code", [200, 202])
def test_sync_get_research_usage_absent_from_response(sync_interceptor, sync_client, code):
    payload = {"request_id": "test-request-123", "status": "pending", "response_time": 0.1}
    sync_interceptor.set_response(code, json=payload)
    assert sync_client.get_research("test-request-123", include_usage=True) == payload


@pytest.mark.parametrize("code", [200, 202])
def test_async_get_research_usage_absent_from_response(async_interceptor, async_client, code):
    payload = {"request_id": "test-request-123", "status": "pending", "response_time": 0.1}
    async_interceptor.set_response(code, json=payload)
    assert asyncio.run(async_client.get_research("test-request-123", include_usage=True)) == payload


@pytest.mark.parametrize("flag", ["false", "true", "", 0, 1, 0.0, [], {}, object()])
def test_sync_get_research_rejects_non_boolean_usage(sync_interceptor, sync_client, flag):
    with pytest.raises(TypeError, match="include_usage must be a bool or None"):
        sync_client.get_research("test-request-123", include_usage=flag)
    assert sync_interceptor.get_request() is None


@pytest.mark.parametrize("flag", ["false", "true", "", 0, 1, 0.0, [], {}, object()])
def test_async_get_research_rejects_non_boolean_usage(async_interceptor, async_client, flag):
    with pytest.raises(TypeError, match="include_usage must be a bool or None"):
        asyncio.run(async_client.get_research("test-request-123", include_usage=flag))
    assert async_interceptor.get_request() is None
