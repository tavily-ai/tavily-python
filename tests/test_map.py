import asyncio

dummy_response = {
    "base_url": "tavily.com",
    "results": [
        "https://www.tavily.com/",
        "https://www.tavily.com/enterprise",
        "https://www.tavily.com/terms",
        "https://www.tavily.com/contact",
    ],
    "response_time": 0.5,
}

def validate_default(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/map"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.json().get('url') == "https://tavily.com"
    assert response == dummy_response

def validate_specific(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/map"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.timeout == 10
    
    request_json = request.json()
    for key, value in {
        "url": "https://tavily.com",
        "max_depth": 2,
        "max_breadth": 3,
        "limit": 5,
        "instructions": "Focus on navigation structure",
        "select_paths": ["/pricing", "/docs"],
        "select_domains": ["tavily.com"],
        "exclude_paths": ["/blog"],
        "exclude_domains": ["example.com"],
        "allow_external": False,
        "include_images": True,
        "categories": ["pricing", "documentation"]
    }.items():
        assert request_json.get(key) == value

    assert response == dummy_response

def test_sync_map_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.map("https://tavily.com")
    request = sync_interceptor.get_request()
    validate_default(request, response)

def test_sync_map_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.map(
        url="https://tavily.com",
        max_depth=2,
        max_breadth=3,
        limit=5,
        instructions="Focus on navigation structure",
        select_paths=["/pricing", "/docs"],
        select_domains=["tavily.com"],
        exclude_paths=["/blog"],
        exclude_domains=["example.com"],
        allow_external=False,
        include_images=True,
        categories=["pricing", "documentation"],
        timeout=10
    )

    request = sync_interceptor.get_request()
    validate_specific(request, response)

def test_async_map_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.map("https://tavily.com"))
    request = async_interceptor.get_request()
    validate_default(request, response)

def test_async_map_specific(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.map(
        url="https://tavily.com",
        max_depth=2,
        max_breadth=3,
        limit=5,
        instructions="Focus on navigation structure",
        select_paths=["/pricing", "/docs"],
        select_domains=["tavily.com"],
        exclude_paths=["/blog"],
        exclude_domains=["example.com"],
        allow_external=False,
        include_images=True,
        categories=["pricing", "documentation"],
        timeout=10
    ))

    request = async_interceptor.get_request()
    validate_specific(request, response)
