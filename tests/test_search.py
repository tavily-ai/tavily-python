import asyncio

dummy_response = {
        "query": "What is Tavily?",
        "follow_up_questions": None,
        "answer": None,
        "images": [],
        "results": [
            {
                "title": "Tavily",
                "url": "https://tavily.com",
                "content": "Connect Your LLM to the Web Empowering your AI applications with " \
                           "real-time, accurate search results tailored for LLMs and RAG.",
                "score": 0.99,
                "raw_content": None
            }
        ],
        "response_time": 1.5
    }

def validate_default(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/search"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.json().get('query') == "What is Tavily?"
    assert response == dummy_response

def validate_specific(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/search"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.timeout == 10
    
    request_json = request.json()
    for key, value in {
        "query": "What is Tavily?",
        "search_depth": "advanced",
        "topic": "news",
        "days": 5,
        "max_results": 10,
        "include_domains": ["tavily.com"],
        "exclude_domains": ["example.com"],
        "include_answer": "advanced",
        "include_raw_content": True,
        "include_images": True
    }.items():
        assert request_json.get(key) == value

    assert response == dummy_response

def test_sync_search_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.search("What is Tavily?")
    request = sync_interceptor.get_request()
    validate_default(request, response)

def test_sync_search_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.search(
        "What is Tavily?",
        search_depth="advanced",
        topic="news",
        days=5,
        max_results=10,
        include_domains=["tavily.com"],
        exclude_domains=["example.com"],
        include_answer="advanced",
        include_raw_content=True,
        include_images=True,
        timeout=10
    )

    request = sync_interceptor.get_request()
    validate_specific(request, response)

def test_async_search_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.search("What is Tavily?"))
    request = async_interceptor.get_request()
    validate_default(request, response)

def test_async_search_specific(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.search(
        "What is Tavily?",
        search_depth="advanced",
        topic="news",
        days=5,
        max_results=10,
        include_domains=["tavily.com"],
        exclude_domains=["example.com"],
        include_answer="advanced",
        include_raw_content=True,
        include_images=True,
        timeout=10
    ))

    request = async_interceptor.get_request()
    validate_specific(request, response)
