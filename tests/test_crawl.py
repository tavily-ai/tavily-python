import asyncio

dummy_response = {
    "base_url": "tavily.com",
    "results": [
        {
            "url": "https://www.tavily.com/",
            "raw_content": "Tavily page content",
            "images": []
        },
    ],
    "response_time": 1.5
}

def validate_default(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/crawl"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.json().get('url') == "https://tavily.com"
    assert response == dummy_response

def validate_specific(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/crawl"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.timeout == 10
    
    request_json = request.json()
    for key, value in {
        "url": "https://tavily.com",
        "max_depth": 2,
        "max_breadth": 3,
        "limit": 5,
        "instructions": "Focus on pricing pages",
        "select_paths": ["/privacy", "/terms"],
        "select_domains": ["tavily.com"],
        "exclude_paths": ["/contact"],
        "exclude_domains": ["example.com"],
        "allow_external": False,
        "include_images": True,
        "categories": ["pricing", "documentation"],
        "extract_depth": "advanced"
    }.items():
        assert request_json.get(key) == value

    assert response == dummy_response

def test_sync_crawl_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.crawl("https://tavily.com")
    request = sync_interceptor.get_request()
    validate_default(request, response)

def test_sync_crawl_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.crawl(
        url="https://tavily.com",
        max_depth=2,
        max_breadth=3,
        limit=5,
        instructions="Focus on pricing pages",
        select_paths=["/privacy", "/terms"],
        select_domains=["tavily.com"],
        exclude_paths=["/contact"],
        exclude_domains=["example.com"],
        allow_external=False,
        include_images=True,
        categories=["pricing", "documentation"],
        extract_depth="advanced",
        timeout=10
    )

    request = sync_interceptor.get_request()
    validate_specific(request, response)

def test_async_crawl_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.crawl("https://tavily.com"))
    request = async_interceptor.get_request()
    validate_default(request, response)

def test_async_crawl_specific(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.crawl(
        url="https://tavily.com",
        max_depth=2,
        max_breadth=3,
        limit=5,
        instructions="Focus on pricing pages",
        select_paths=["/privacy", "/terms"],
        select_domains=["tavily.com"],
        exclude_paths=["/contact"],
        exclude_domains=["example.com"],
        allow_external=False,
        include_images=True,
        categories=["pricing", "documentation"],
        extract_depth="advanced",
        timeout=10
    ))

    request = async_interceptor.get_request()
    validate_specific(request, response)
