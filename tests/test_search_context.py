import asyncio
import json

import pytest
import tiktoken

from tavily.config import DEFAULT_MODEL_ENCODING
from tavily.utils import get_total_tokens_from_string


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
def test_sync_search_context_preserves_content_and_respects_item_budget(
    sync_interceptor, sync_client, content
):
    source = {"url": "https://example.com/tokenizer", "content": content}
    sync_interceptor.set_response(200, json={"results": [source]})
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    item_budget = len(encoding.encode_ordinary(json.dumps(source)))

    with pytest.warns(DeprecationWarning):
        context = sync_client.get_search_context("tokenizer documentation", max_tokens=item_budget)
    assert json.loads(context) == [source]

    with pytest.warns(DeprecationWarning):
        context = sync_client.get_search_context("tokenizer documentation", max_tokens=item_budget - 1)
    assert json.loads(context) == []


@pytest.mark.parametrize("content", CONTENTS)
def test_async_search_context_preserves_content_and_respects_item_budget(
    async_interceptor, async_client, content
):
    source = {"url": "https://example.com/tokenizer", "content": content}
    async_interceptor.set_response(200, json={"results": [source]})
    encoding = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    item_budget = len(encoding.encode_ordinary(json.dumps(source)))

    async def get_contexts():
        async with async_client:
            context = await async_client.get_search_context(
                "tokenizer documentation", max_tokens=item_budget
            )
            limited_context = await async_client.get_search_context(
                "tokenizer documentation", max_tokens=item_budget - 1
            )
        return context, limited_context

    context, limited_context = asyncio.run(get_contexts())
    assert json.loads(context) == [source]
    assert json.loads(limited_context) == []
