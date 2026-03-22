import pytest
from tests.request_intercept import intercept_requests, clear_interceptor
import tavily.tavily as sync_tavily
from tavily.refrag import TavilyRefragClient, RefragChunk, RefragContext


dummy_search_response = {
    "query": "What is REFRAG?",
    "answer": None,
    "images": [],
    "results": [
        {
            "title": "REFRAG Paper",
            "url": "https://arxiv.org/abs/2509.01092",
            "content": "REFRAG is an efficient decoding framework that compresses senses and expands",
            "score": 0.95,
            "raw_content": None,
        },
        {
            "title": "RAG Overview",
            "url": "https://example.com/rag",
            "content": "Retrieval augmented generation improves LLM accuracy",
            "score": 0.88,
            "raw_content": None,
        },
    ],
    "response_time": 0.8,
}


@pytest.fixture
def interceptor():
    yield intercept_requests(sync_tavily)
    clear_interceptor(sync_tavily)


def _dummy_encoder(token_lists):
    """Return a fixed-length embedding per chunk (dimension = 4)."""
    return [[float(len(tl)), 0.1, 0.2, 0.3] for tl in token_lists]


def _dummy_expansion_policy(chunk_embeddings, query_embedding=None):
    """Expand the first chunk, compress the rest."""
    return [i == 0 for i in range(len(chunk_embeddings))]


# ---------------------------------------------------------------------------
# Constructor tests
# ---------------------------------------------------------------------------

class TestConstructor:
    def test_default_chunk_size(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test")
        assert client.chunk_size == 16

    def test_custom_chunk_size(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=32)
        assert client.chunk_size == 32

    def test_invalid_chunk_size_raises(self, interceptor):
        with pytest.raises(ValueError, match="chunk_size must be a positive integer"):
            TavilyRefragClient(api_key="tvly-test", chunk_size=0)

    def test_no_encoder_by_default(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test")
        assert client.encoder_function is None


# ---------------------------------------------------------------------------
# chunk_passages tests
# ---------------------------------------------------------------------------

class TestChunkPassages:
    def test_basic_chunking(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=4)
        passages = [
            {"content": "one two three four five six seven eight", "url": "https://a.com", "score": 0.9}
        ]
        chunks = client.chunk_passages(passages)

        assert len(chunks) >= 2
        assert all(isinstance(c, RefragChunk) for c in chunks)
        for c in chunks:
            assert len(c.tokens) <= 4
            assert c.source_url == "https://a.com"
            assert c.source_score == 0.9
            assert c.embedding is None
            assert c.expand is False

    def test_empty_content_skipped(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=4)
        passages = [{"content": "", "url": "https://a.com", "score": 0.5}]
        chunks = client.chunk_passages(passages)
        assert len(chunks) == 0

    def test_multiple_passages(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=4)
        passages = [
            {"content": "alpha beta gamma delta", "url": "https://a.com", "score": 0.9},
            {"content": "epsilon zeta", "url": "https://b.com", "score": 0.7},
        ]
        chunks = client.chunk_passages(passages)
        urls = [c.source_url for c in chunks]
        assert "https://a.com" in urls
        assert "https://b.com" in urls

    def test_chunk_size_override(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=100)
        passages = [{"content": "a b c d e f g h", "url": "https://a.com", "score": 0.5}]
        chunks_big = client.chunk_passages(passages, chunk_size=100)
        chunks_small = client.chunk_passages(passages, chunk_size=2)
        assert len(chunks_small) > len(chunks_big)

    def test_missing_content_key(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=4)
        passages = [{"url": "https://a.com"}]
        chunks = client.chunk_passages(passages)
        assert len(chunks) == 0


# ---------------------------------------------------------------------------
# encode_chunks tests
# ---------------------------------------------------------------------------

class TestEncodeChunks:
    def test_encode_populates_embeddings(self, interceptor):
        client = TavilyRefragClient(
            api_key="tvly-test", chunk_size=4, encoder_function=_dummy_encoder
        )
        passages = [{"content": "one two three four five six", "url": "https://a.com", "score": 0.9}]
        chunks = client.chunk_passages(passages)
        assert all(c.embedding is None for c in chunks)

        client.encode_chunks(chunks)
        assert all(c.embedding is not None for c in chunks)
        assert len(chunks[0].embedding) == 4

    def test_encode_without_encoder_raises(self, interceptor):
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=4)
        passages = [{"content": "hello world", "url": "https://a.com", "score": 0.9}]
        chunks = client.chunk_passages(passages)

        with pytest.raises(RuntimeError, match="encoder_function must be provided"):
            client.encode_chunks(chunks)

    def test_encoder_receives_correct_tokens(self, interceptor):
        received = []

        def tracking_encoder(token_lists):
            received.extend(token_lists)
            return [[0.0] * 4 for _ in token_lists]

        client = TavilyRefragClient(
            api_key="tvly-test", chunk_size=4, encoder_function=tracking_encoder
        )
        passages = [{"content": "one two three four five six", "url": "https://a.com", "score": 0.9}]
        chunks = client.chunk_passages(passages)
        client.encode_chunks(chunks)

        assert len(received) == len(chunks)
        for token_list, chunk in zip(received, chunks):
            assert token_list == chunk.tokens


# ---------------------------------------------------------------------------
# apply_expansion_policy tests
# ---------------------------------------------------------------------------

class TestExpansionPolicy:
    def test_default_policy_compresses_all(self, interceptor):
        client = TavilyRefragClient(
            api_key="tvly-test", chunk_size=4, encoder_function=_dummy_encoder
        )
        passages = [{"content": "one two three four five six seven eight", "url": "https://a.com", "score": 0.9}]
        chunks = client.chunk_passages(passages)
        client.encode_chunks(chunks)
        client.apply_expansion_policy(chunks)

        assert all(c.expand is False for c in chunks)

    def test_custom_policy_applied(self, interceptor):
        client = TavilyRefragClient(
            api_key="tvly-test",
            chunk_size=4,
            encoder_function=_dummy_encoder,
            expansion_policy=_dummy_expansion_policy,
        )
        passages = [{"content": "one two three four five six seven eight", "url": "https://a.com", "score": 0.9}]
        chunks = client.chunk_passages(passages)
        client.encode_chunks(chunks)
        client.apply_expansion_policy(chunks)

        assert chunks[0].expand is True
        assert all(c.expand is False for c in chunks[1:])

    def test_policy_without_embeddings_raises(self, interceptor):
        client = TavilyRefragClient(
            api_key="tvly-test",
            chunk_size=4,
            encoder_function=_dummy_encoder,
            expansion_policy=_dummy_expansion_policy,
        )
        passages = [{"content": "hello world tokens here", "url": "https://a.com", "score": 0.9}]
        chunks = client.chunk_passages(passages)

        with pytest.raises(ValueError, match="must have embeddings"):
            client.apply_expansion_policy(chunks)


# ---------------------------------------------------------------------------
# RefragContext dataclass tests
# ---------------------------------------------------------------------------

class TestRefragContext:
    def test_compressed_and_expanded_properties(self):
        chunks = [
            RefragChunk(text="a", tokens=[1], embedding=[0.1], expand=False),
            RefragChunk(text="b", tokens=[2], embedding=[0.2], expand=True),
            RefragChunk(text="c", tokens=[3], embedding=[0.3], expand=False),
        ]
        ctx = RefragContext(query="test", chunks=chunks, chunk_size=1)

        assert len(ctx.compressed_chunks) == 2
        assert len(ctx.expanded_chunks) == 1
        assert ctx.expanded_chunks[0].text == "b"

    def test_empty_chunks(self):
        ctx = RefragContext(query="test", chunks=[], chunk_size=16)
        assert ctx.compressed_chunks == []
        assert ctx.expanded_chunks == []


# ---------------------------------------------------------------------------
# prepare_context (end-to-end) tests
# ---------------------------------------------------------------------------

class TestPrepareContext:
    def test_full_pipeline(self, interceptor):
        interceptor.set_response(200, json=dummy_search_response)
        client = TavilyRefragClient(
            api_key="tvly-test",
            chunk_size=4,
            encoder_function=_dummy_encoder,
            expansion_policy=_dummy_expansion_policy,
        )

        ctx = client.prepare_context("What is REFRAG?", max_results=5)

        assert isinstance(ctx, RefragContext)
        assert ctx.query == "What is REFRAG?"
        assert ctx.chunk_size == 4
        assert len(ctx.chunks) > 0
        assert all(c.embedding is not None for c in ctx.chunks)
        assert ctx.chunks[0].expand is True
        assert ctx.metadata.get("response_time") == 0.8

        request = interceptor.get_request()
        assert request.method == "POST"
        assert request.url == "https://api.tavily.com/search"
        assert request.json()["query"] == "What is REFRAG?"

    def test_pipeline_without_encoder(self, interceptor):
        interceptor.set_response(200, json=dummy_search_response)
        client = TavilyRefragClient(api_key="tvly-test", chunk_size=4)

        ctx = client.prepare_context("What is REFRAG?", encode=True)

        assert len(ctx.chunks) > 0
        assert all(c.embedding is None for c in ctx.chunks)
        assert all(c.expand is False for c in ctx.chunks)

    def test_pipeline_skip_encode(self, interceptor):
        interceptor.set_response(200, json=dummy_search_response)
        client = TavilyRefragClient(
            api_key="tvly-test",
            chunk_size=4,
            encoder_function=_dummy_encoder,
        )

        ctx = client.prepare_context("What is REFRAG?", encode=False)

        assert all(c.embedding is None for c in ctx.chunks)

    def test_pipeline_encode_but_skip_policy(self, interceptor):
        interceptor.set_response(200, json=dummy_search_response)
        client = TavilyRefragClient(
            api_key="tvly-test",
            chunk_size=4,
            encoder_function=_dummy_encoder,
            expansion_policy=_dummy_expansion_policy,
        )

        ctx = client.prepare_context("What is REFRAG?", apply_policy=False)

        assert all(c.embedding is not None for c in ctx.chunks)
        assert all(c.expand is False for c in ctx.chunks)

    def test_search_kwargs_forwarded(self, interceptor):
        interceptor.set_response(200, json=dummy_search_response)
        client = TavilyRefragClient(
            api_key="tvly-test",
            chunk_size=4,
            encoder_function=_dummy_encoder,
        )

        client.prepare_context(
            "What is REFRAG?",
            max_results=3,
            search_depth="advanced",
            topic="general",
        )

        request = interceptor.get_request()
        body = request.json()
        assert body["search_depth"] == "advanced"
        assert body["topic"] == "general"

    def test_empty_results(self, interceptor):
        interceptor.set_response(200, json={
            "query": "nothing",
            "results": [],
            "response_time": 0.1,
        })
        client = TavilyRefragClient(
            api_key="tvly-test", chunk_size=4, encoder_function=_dummy_encoder
        )
        ctx = client.prepare_context("nothing")
        assert len(ctx.chunks) == 0
        assert ctx.compressed_chunks == []
        assert ctx.expanded_chunks == []
