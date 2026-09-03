import asyncio

dummy_response = {
    "success": True,
    "feedback_id": "fb_123",
    "response_time": 0.02
}

def validate_default(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/feedback"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.json().get('request_id') == "req_1"
    assert response == dummy_response

def validate_specific(request, response):
    assert request.method == "POST"
    assert request.url == "https://api.tavily.com/feedback"
    assert request.headers["Authorization"] == "Bearer tvly-test"
    assert request.headers["X-Client-Source"] == "tavily-python"
    assert request.timeout == 10

    request_json = request.json()
    for key, value in {
        "session_id": "sess_1",
        "request_id": "req_1",
        "agent_score": 0.9,
        "human_score": "like",
        "extra_scores": [{"label": "freshness", "value": 0.8}],
        "comment": "Great results",
        "response_delivered": "The answer we produced",
        "used_urls": ["https://tavily.com"],
        "used_ids": ["r1"],
        "used_citations": ["Tavily is a search API"],
        "urls_scores": [{"id": "r1", "agent_score": 0.9, "comment": "Strong match"}],
    }.items():
        assert request_json.get(key) == value

    assert response == dummy_response

def test_sync_feedback_defaults(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.feedback(request_id="req_1")
    request = sync_interceptor.get_request()
    validate_default(request, response)

def test_sync_feedback_specific(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, json=dummy_response)
    response = sync_client.feedback(
        session_id="sess_1",
        request_id="req_1",
        agent_score=0.9,
        human_score="like",
        extra_scores=[{"label": "freshness", "value": 0.8}],
        comment="Great results",
        response_delivered="The answer we produced",
        used_urls=["https://tavily.com"],
        used_ids=["r1"],
        used_citations=["Tavily is a search API"],
        urls_scores=[{"id": "r1", "agent_score": 0.9, "comment": "Strong match"}],
        timeout=10
    )

    request = sync_interceptor.get_request()
    validate_specific(request, response)

def test_async_feedback_defaults(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.feedback(request_id="req_1"))
    request = async_interceptor.get_request()
    validate_default(request, response)

def test_async_feedback_specific(async_interceptor, async_client):
    async_interceptor.set_response(200, json=dummy_response)
    response = asyncio.run(async_client.feedback(
        session_id="sess_1",
        request_id="req_1",
        agent_score=0.9,
        human_score="like",
        extra_scores=[{"label": "freshness", "value": 0.8}],
        comment="Great results",
        response_delivered="The answer we produced",
        used_urls=["https://tavily.com"],
        used_ids=["r1"],
        used_citations=["Tavily is a search API"],
        urls_scores=[{"id": "r1", "agent_score": 0.9, "comment": "Strong match"}],
        timeout=10
    ))

    request = async_interceptor.get_request()
    validate_specific(request, response)
