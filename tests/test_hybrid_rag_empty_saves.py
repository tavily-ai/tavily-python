from unittest.mock import Mock

import pytest

from tavily import TavilyHybridClient


@pytest.fixture
def hybrid_client():
    collection = Mock()
    collection.list_search_indexes.return_value = [{
        "name": "test-index",
        "type": "vectorSearch",
        "latestDefinition": {"fields": [{
            "path": "embedding",
            "type": "vector",
            "similarity": "cosine",
        }]},
    }]
    collection.aggregate.return_value = [{"content": "Local result", "origin": "local"}]
    embedding = Mock(side_effect=lambda texts, kind: [[1.0, 0.0] for _ in texts])
    ranking = Mock(side_effect=lambda query, results, limit: results[:limit])
    client = TavilyHybridClient(
        api_key="tvly-test",
        db_provider="mongodb",
        collection=collection,
        index="test-index",
        content_field="text",
        embeddings_field="embedding",
        embedding_function=embedding,
        ranking_function=ranking,
    )
    client.tavily.search = Mock(return_value={"results": []})
    yield client
    client.tavily.close()


def test_empty_foreign_results_do_not_embed_or_write(hybrid_client):
    results = hybrid_client.search("query", save_foreign=True)

    assert results == [{"content": "Local result", "origin": "local"}]
    hybrid_client.embedding_function.assert_called_once_with(["query"], "search_query")
    hybrid_client.collection.insert_many.assert_not_called()


@pytest.mark.parametrize("discard", [None, {}])
def test_all_transformed_foreign_results_discarded_do_not_write(hybrid_client, discard):
    hybrid_client.tavily.search.return_value = {
        "results": [{"content": "Web result", "score": 0.9}]
    }
    transform = Mock(return_value=discard)

    results = hybrid_client.search("query", save_foreign=transform)

    assert results[-1] == {"content": "Web result", "score": 0.9, "origin": "foreign"}
    transform.assert_called_once_with({
        "content": "Web result", "score": 0.9, "embeddings": [1.0, 0.0]
    })
    hybrid_client.collection.insert_many.assert_not_called()


def test_nonempty_foreign_results_saved_with_configured_fields(hybrid_client):
    hybrid_client.tavily.search.return_value = {
        "results": [{"content": "Web result", "score": 0.9}]
    }

    results = hybrid_client.search("query", save_foreign=True)

    assert len(results) == 2
    hybrid_client.collection.insert_many.assert_called_once_with([
        {"text": "Web result", "embedding": [1.0, 0.0]}
    ])


def test_transform_keeps_only_nonempty_documents(hybrid_client):
    hybrid_client.tavily.search.return_value = {
        "results": [{"content": "Discard", "score": 0.8},
                    {"content": "Keep", "score": 0.9}]
    }
    transform = Mock(side_effect=[None, {"text": "Kept", "custom": True}])

    results = hybrid_client.search("query", save_foreign=transform)

    assert len(results) == 3
    assert transform.call_count == 2
    hybrid_client.collection.insert_many.assert_called_once_with([
        {"text": "Kept", "custom": True}
    ])


def test_save_disabled_does_not_embed_documents_or_write(hybrid_client):
    hybrid_client.tavily.search.return_value = {
        "results": [{"content": "Web result", "score": 0.9}]
    }

    assert len(hybrid_client.search("query", save_foreign=False)) == 2
    hybrid_client.embedding_function.assert_called_once_with(["query"], "search_query")
    hybrid_client.collection.insert_many.assert_not_called()


def test_no_combined_results_return_empty_without_writing(hybrid_client):
    hybrid_client.collection.aggregate.return_value = []

    assert hybrid_client.search("query", save_foreign=True) == []
    hybrid_client.ranking_function.assert_not_called()
    hybrid_client.collection.insert_many.assert_not_called()
