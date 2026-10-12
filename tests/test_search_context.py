import asyncio
import json

import pytest
import tiktoken

from tavily.config import DEFAULT_MODEL_ENCODING
from tavily.utils import get_max_items_from_list, get_total_tokens_from_string


CONTENTS = [
    "The tokenizer uses <|endoftext|> to mark the end of a document.",
    "Fill-in-the-middle uses <|fim_prefix|>, <|fim_middle|>, and <|fim_suffix|>.",
    "Ordinary retrieved text without special token spellings.",
]


@pytest.mark.parametrize("content", CONTENTS)
def test_token_count_treats_retrieved_content_as_ordinary_text(content):
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)

    assert get_total_tokens_from_string(content) == len(encoding.encode_ordinary(content))


@pytest.mark.parametrize("content", CONTENTS)
def test_sync_search_context_preserves_content_and_respects_json_budget(
    sync_interceptor, sync_client, content
):
    source = {"url": "https://example.com/tokenizer", "content": content}
    sync_interceptor.set_response(200, json={"results": [source]})
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    context_budget = len(encoding.encode_ordinary(json.dumps([source])))

    with pytest.warns(DeprecationWarning):
        context = sync_client.get_search_context("tokenizer documentation", max_tokens=context_budget)
    assert json.loads(context) == [source]

    with pytest.warns(DeprecationWarning):
        context = sync_client.get_search_context("tokenizer documentation", max_tokens=context_budget - 1)
    assert json.loads(context) == []


@pytest.mark.parametrize("content", CONTENTS)
def test_async_search_context_preserves_content_and_respects_json_budget(
    async_interceptor, async_client, content
):
    source = {"url": "https://example.com/tokenizer", "content": content}
    async_interceptor.set_response(200, json={"results": [source]})
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    context_budget = len(encoding.encode_ordinary(json.dumps([source])))

    async def get_contexts():
        async with async_client:
            context = await async_client.get_search_context(
                "tokenizer documentation", max_tokens=context_budget
            )
            limited_context = await async_client.get_search_context(
                "tokenizer documentation", max_tokens=context_budget - 1
            )
        return context, limited_context

    context, limited_context = asyncio.run(get_contexts())
    assert json.loads(context) == [source]
    assert json.loads(limited_context) == []


SOURCES = [
    {"url": "https://example.com/a", "content": "Ordinary source text."},
    {"url": "https://example.com/b", "content": "Another relevant source."},
    {"url": "https://example.com/c", "content": "中文检索结果，也需要遵守上下文预算。"},
]


@pytest.mark.parametrize("source_count", [1, 2, 3])
def test_sync_search_context_counts_the_complete_json_array(
    sync_interceptor, sync_client, source_count
):
    sources = SOURCES[:source_count]
    sync_interceptor.set_response(200, json={"results": sources})
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    context_budget = len(encoding.encode_ordinary(json.dumps(sources)))

    with pytest.warns(DeprecationWarning):
        context = sync_client.get_search_context("retrieval", max_tokens=context_budget)
    assert json.loads(context) == sources
    assert len(encoding.encode_ordinary(context)) == context_budget

    with pytest.warns(DeprecationWarning):
        context = sync_client.get_search_context("retrieval", max_tokens=context_budget - 1)
    assert json.loads(context) == sources[:-1]
    assert len(encoding.encode_ordinary(context)) <= context_budget - 1


@pytest.mark.parametrize("source_count", [1, 2, 3])
def test_async_search_context_counts_the_complete_json_array(
    async_interceptor, async_client, source_count
):
    sources = SOURCES[:source_count]
    async_interceptor.set_response(200, json={"results": sources})
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    context_budget = len(encoding.encode_ordinary(json.dumps(sources)))

    async def get_contexts():
        async with async_client:
            context = await async_client.get_search_context("retrieval", max_tokens=context_budget)
            limited_context = await async_client.get_search_context(
                "retrieval", max_tokens=context_budget - 1
            )
        return context, limited_context

    context, limited_context = asyncio.run(get_contexts())
    assert json.loads(context) == sources
    assert len(encoding.encode_ordinary(context)) == context_budget
    assert json.loads(limited_context) == sources[:-1]
    assert len(encoding.encode_ordinary(limited_context)) <= context_budget - 1


@pytest.mark.parametrize("max_tokens", [0, -1])
def test_non_positive_context_budget_preserves_empty_result(max_tokens):
    assert get_max_items_from_list(SOURCES, max_tokens=max_tokens) == []
