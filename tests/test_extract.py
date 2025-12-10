import asyncio

dummy_response = {
    "results": [
        {
            "url": "https://tavily.com",
            "raw_content": "Example content",
            "images": []
        }
    ],
    "failed_results": [],
    "response_time": 0.3
}

def validate_default(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/extract"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    request_json = request.json()
    assert request_json.get("urls") == ["https://tavily.com"]
    assert request_json.get("include_usage") is False
    assert response == dummy_response

def validate_specific(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/extract"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.timeout == 15

    request_json = request.json()
    for key, value in {
        "urls": ["https://tavily.com"],
        "include_images": True,
        "extract_depth": "advanced",
        "format": "markdown",
        "include_favicon": True,
        "include_usage": True,
    }.items():
        assert request_json.get(key) == value

    assert response == dummy_response

def test_sync_extract_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.extract(["https://tavily.com"])
    request = sync_interceptor.get_request()
    validate_default(request, response)

def test_sync_extract_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.extract(
        ["https://tavily.com"],
        include_images=True,
        extract_depth="advanced",
        format="markdown",
        include_favicon=True,
        include_usage=True,
        timeout=15
    )
    request = sync_interceptor.get_request()
    validate_specific(request, response)

def test_async_extract_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.extract(["https://tavily.com"]))
    request = async_interceptor.get_request()
    validate_default(request, response)

def test_async_extract_specific(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.extract(
        ["https://tavily.com"],
        include_images=True,
        extract_depth="advanced",
        format="markdown",
        include_favicon=True,
        include_usage=True,
        timeout=15
    ))
    request = async_interceptor.get_request()
    validate_specific(request, response)
