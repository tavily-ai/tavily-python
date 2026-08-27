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

def validate_specific(request, response, expected_response=dummy_response):
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
        "include_images": True,
        "exact_match": True
    }.items():
        assert request_json.get(key) == value

    assert response == expected_response

def test_sync_search_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.search("What is Tavily?")
    request = sync_interceptor.get_request()
    validate_default(request, response)

def test_sync_search_specific(sync_interceptor, sync_client):
    response_with_out_of_scope_results = {
        **dummy_response,
        "results": [
            {"url": "https://tavily.com/allowed", "title": "Root domain"},
            {"url": "https://docs.tavily.com/allowed", "title": "Subdomain"},
            {"url": "https://example.com/outside", "title": "Outside domain"},
            {"url": "https://not-tavily.com/outside", "title": "Similar suffix"},
            {"url": "not a URL", "title": "Malformed URL"},
        ],
    }
    sync_interceptor.set_response(200, json=response_with_out_of_scope_results)
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
        exact_match=True,
        timeout=10
    )

    request = sync_interceptor.get_request()
    expected_response = {
        **response_with_out_of_scope_results,
        "results": response_with_out_of_scope_results["results"][:2],
    }
    validate_specific(request, response, expected_response)
    assert [result["title"] for result in response["results"]] == ["Root domain", "Subdomain"]

def test_async_search_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.search("What is Tavily?"))
    request = async_interceptor.get_request()
    validate_default(request, response)

def test_async_search_specific(async_interceptor, async_client):
    response_with_out_of_scope_results = {
        **dummy_response,
        "results": [
            {"url": "https://tavily.com/allowed", "title": "Root domain"},
            {"url": "https://docs.tavily.com/allowed", "title": "Subdomain"},
            {"url": "https://example.com/outside", "title": "Outside domain"},
            {"url": "https://not-tavily.com/outside", "title": "Similar suffix"},
            {"url": "not a URL", "title": "Malformed URL"},
        ],
    }
    async_interceptor.set_response(200, json=response_with_out_of_scope_results)
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
        exact_match=True,
        timeout=10
    ))

    request = async_interceptor.get_request()
    expected_response = {
        **response_with_out_of_scope_results,
        "results": response_with_out_of_scope_results["results"][:2],
    }
    validate_specific(request, response, expected_response)
    assert [result["title"] for result in response["results"]] == ["Root domain", "Subdomain"]


def test_sync_search_without_domain_filter_preserves_results(sync_interceptor, sync_client):
    response_with_out_of_scope_results = {
        **dummy_response,
        "results": [
            {"url": "https://tavily.com/allowed", "title": "Allowed"},
            {"url": "https://example.com/outside", "title": "Outside"},
        ],
    }
    sync_interceptor.set_response(200, json=response_with_out_of_scope_results)

    response = sync_client.search("What is Tavily?")

    assert response["results"] == response_with_out_of_scope_results["results"]

def test_sync_search_exact_match_not_sent_by_default(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search("What is Tavily?")
    request = sync_interceptor.get_request()
    assert "exact_match" not in request.json()

def test_sync_search_exact_match_true(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search("What is Tavily?", exact_match=True)
    request = sync_interceptor.get_request()
    assert request.json()["exact_match"] is True

def test_sync_search_exact_match_false(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search("What is Tavily?", exact_match=False)
    request = sync_interceptor.get_request()
    assert request.json()["exact_match"] is False

def test_async_search_exact_match_not_sent_by_default(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search("What is Tavily?"))
    request = async_interceptor.get_request()
    assert "exact_match" not in request.json()

def test_async_search_exact_match_true(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search("What is Tavily?", exact_match=True))
    request = async_interceptor.get_request()
    assert request.json()["exact_match"] is True

def test_async_search_exact_match_false(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search("What is Tavily?", exact_match=False))
    request = async_interceptor.get_request()
    assert request.json()["exact_match"] is False

def test_sync_search_exact_match_query_quotes_escaped_in_payload(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search('"John Smith" CEO Acme Corp', exact_match=True)
    request = sync_interceptor.get_request()
    # The raw JSON payload should have escaped quotes for the quoted phrase
    assert r'\"John Smith\"' in request.body
    # But the parsed query should preserve the original quotes
    assert request.json()["query"] == '"John Smith" CEO Acme Corp'

def test_async_search_exact_match_query_quotes_escaped_in_payload(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search('"John Smith" CEO Acme Corp', exact_match=True))
    request = async_interceptor.get_request()
    assert r'\"John Smith\"' in request.body
    assert request.json()["query"] == '"John Smith" CEO Acme Corp'

def test_sync_search_language_not_sent_by_default(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search("What is Tavily?")
    request = sync_interceptor.get_request()
    assert "language" not in request.json()
    assert "filter_by_language" not in request.json()

def test_sync_search_language(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search("What is Tavily?", language="french", filter_by_language=True)
    request = sync_interceptor.get_request()
    assert request.json()["language"] == "french"
    assert request.json()["filter_by_language"] is True

def test_async_search_language_not_sent_by_default(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search("What is Tavily?"))
    request = async_interceptor.get_request()
    assert "language" not in request.json()
    assert "filter_by_language" not in request.json()

def test_async_search_language(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search("What is Tavily?", language="french", filter_by_language=True))
    request = async_interceptor.get_request()
    assert request.json()["language"] == "french"
    assert request.json()["filter_by_language"] is True

def test_sync_search_language_only_no_filter(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    sync_client.search("What is Tavily?", language="french")
    request = sync_interceptor.get_request()
    assert request.json()["language"] == "french"
    assert "filter_by_language" not in request.json()

def test_async_search_language_only_no_filter(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    asyncio.run(async_client.search("What is Tavily?", language="french"))
    request = async_interceptor.get_request()
    assert request.json()["language"] == "french"
    assert "filter_by_language" not in request.json()
