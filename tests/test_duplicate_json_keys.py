import asyncio

import pytest

from tavily.utils import parse_json_response


def test_parse_json_response_merges_duplicate_list_keys():
    raw = (
        '{"query": "red fox", "images": ["a.jpg", "b.jpg"], '
        '"images": ["c.jpg"], "results": []}'
    )
    parsed = parse_json_response(raw)
    assert parsed["images"] == ["a.jpg", "b.jpg", "c.jpg"]
    assert parsed["results"] == []


def test_parse_json_response_keeps_last_value_for_non_list_duplicate_keys():
    # Non-list duplicate keys keep the standard JSON last-value-wins behavior.
    raw = '{"status": "pending", "status": "completed"}'
    parsed = parse_json_response(raw)
    assert parsed["status"] == "completed"


def test_parse_json_response_no_duplicates_unaffected():
    raw = '{"query": "red fox", "images": ["a.jpg"], "results": []}'
    parsed = parse_json_response(raw)
    assert parsed["images"] == ["a.jpg"]


def test_parse_json_response_raises_on_invalid_json():
    with pytest.raises(ValueError):
        parse_json_response("not json")


def _duplicate_images_body():
    return (
        '{"query": "red fox", "results": [], '
        '"images": ["https://a.com/1.jpg", "https://a.com/2.jpg"], '
        '"images": ["https://a.com/3.jpg"]}'
    )


def test_sync_search_merges_duplicate_images_key(sync_interceptor, sync_client):
    sync_interceptor.set_response(200, headers={"Content-Type": "application/json"}, body=_duplicate_images_body())
    response = sync_client.search("red fox")
    assert response["images"] == [
        "https://a.com/1.jpg",
        "https://a.com/2.jpg",
        "https://a.com/3.jpg",
    ]


def test_async_search_merges_duplicate_images_key(async_interceptor, async_client):
    async_interceptor.set_response(200, headers={"Content-Type": "application/json"}, body=_duplicate_images_body())
    response = asyncio.run(async_client.search("red fox"))
    assert response["images"] == [
        "https://a.com/1.jpg",
        "https://a.com/2.jpg",
        "https://a.com/3.jpg",
    ]
