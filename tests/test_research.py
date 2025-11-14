import asyncio

BASE_URL = "https://api.tavily.com"

dummy_queued_response = {
    "request_id": "test-request-123",
    "created_at": "2024-01-01T00:00:00Z",
    "status": "pending",
    "task_description": "Research the latest developments in AI",
    "research_depth": "deep"
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
            "content": "Summary of AI research..."
        }
    ]
}

def validate_research_default(request, response):
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/research"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.json().get('task_description') == "Research the latest developments in AI"
    assert response == dummy_queued_response

def validate_research_specific(request, response):
    assert request.method == "POST"
    assert request.url == f"{BASE_URL}/research"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    
    request_json = request.json()
    for key, value in {
        "task_description": "Research the latest developments in AI",
        "research_depth": "deep",
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
    assert response == dummy_research_response

def test_sync_research_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_queued_response)
    response = sync_client.research("Research the latest developments in AI")
    request = sync_interceptor.get_request()
    validate_research_default(request, response)

def test_sync_research_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_queued_response)
    response = sync_client.research(
        task_description="Research the latest developments in AI",
        research_depth="deep",
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
    validate_research_specific(request, response)

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
    response = asyncio.run(async_client.research(
        task_description="Research the latest developments in AI",
        research_depth="deep",
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
    ))

    request = async_interceptor.get_request()
    validate_research_specific(request, response)

def test_async_get_research(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_research_response)
    response = asyncio.run(async_client.get_research("test-request-123"))
    request = async_interceptor.get_request()
    validate_get_research(request, response)

