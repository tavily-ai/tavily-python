import tiktoken
from typing import Optional, List, Dict, Any, Callable, Sequence

import requests
from tavily import TavilyClient
from tavily.config import DEFAULT_MODEL_ENCODING
from .models import RefragChunk, RefragContext


def _default_tokenize(text: str, _encoder=[None]) -> List[int]:
    if _encoder[0] is None:
        _encoder[0] = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    return _encoder[0].encode(text)


def _default_detokenize(tokens: List[int], _encoder=[None]) -> str:
    if _encoder[0] is None:
        _encoder[0] = tiktoken.encoding_for_model(DEFAULT_MODEL_ENCODING)
    return _encoder[0].decode(tokens)


def _default_expansion_policy(
    chunk_embeddings: List[List[float]],
    query_embedding: Optional[List[float]] = None,
) -> List[bool]:
    """Default policy: compress everything (expand nothing)."""
    return [False] * len(chunk_embeddings)


class TavilyRefragClient:
    """Preprocessing adapter that converts Tavily search results into
    REFRAG-compatible chunked and encoded context.

    This client handles the retrieval-to-REFRAG-input pipeline:
    query -> Tavily search -> passage chunking -> encoder -> expansion policy
    -> RefragContext ready for an external REFRAG decoder.

    Each pipeline step is available independently (chunk_passages,
    encode_chunks, apply_expansion_policy) or as a single call
    (prepare_context).

    Parameters:
        api_key: Tavily API key (falls back to TAVILY_API_KEY env var).
        chunk_size: Number of tokens per chunk (k in the REFRAG paper).
            Paper evaluates k=8, 16, 32; default is 16.
        tokenizer_function: ``(text: str) -> list[int]``.
            Defaults to tiktoken with the gpt-3.5-turbo encoding.
        detokenizer_function: ``(tokens: list[int]) -> str``.
            Defaults to tiktoken with the gpt-3.5-turbo encoding.
        encoder_function: ``(chunks: list[list[int]]) -> list[list[float]]``.
            Takes a list of token-ID lists, returns embedding vectors.
            No default — raises if encode_chunks is called without one.
        expansion_policy: ``(chunk_embeddings, query_embedding) -> list[bool]``.
            Returns a boolean mask indicating which chunks to expand.
            Defaults to compressing all chunks (expand nothing).
        api_base_url: Override the Tavily base URL.
        session: Pre-configured requests.Session for HTTP calls.
        **tavily_kwargs: Extra keyword arguments forwarded to TavilyClient.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        chunk_size: int = 16,
        tokenizer_function: Optional[Callable[[str], List[int]]] = None,
        detokenizer_function: Optional[Callable[[List[int]], str]] = None,
        encoder_function: Optional[Callable[[List[List[int]]], List[List[float]]]] = None,
        expansion_policy: Optional[Callable] = None,
        api_base_url: Optional[str] = None,
        session: Optional[requests.Session] = None,
        **tavily_kwargs,
    ):
        if chunk_size < 1:
            raise ValueError("chunk_size must be a positive integer.")

        self.tavily = TavilyClient(
            api_key=api_key,
            api_base_url=api_base_url,
            session=session,
            **tavily_kwargs,
        )
        self.chunk_size = chunk_size
        self.tokenizer_function = tokenizer_function or _default_tokenize
        self.detokenizer_function = detokenizer_function or _default_detokenize
        self.encoder_function = encoder_function
        self.expansion_policy = expansion_policy or _default_expansion_policy

    def chunk_passages(
        self,
        passages: List[Dict[str, Any]],
        chunk_size: Optional[int] = None,
    ) -> List[RefragChunk]:
        """Split retrieved passages into fixed-size token chunks.

        Each Tavily result dict is expected to have at least a ``content``
        key.  The text is tokenized and then split into non-overlapping
        chunks of ``chunk_size`` tokens.  Leftover tokens shorter than
        ``chunk_size`` are kept as a final smaller chunk.

        Args:
            passages: List of Tavily result dicts (must contain ``content``).
            chunk_size: Override the instance-level chunk_size for this call.

        Returns:
            Ordered list of RefragChunk objects.
        """
        k = chunk_size or self.chunk_size
        chunks: List[RefragChunk] = []

        for passage in passages:
            content = passage.get("content", "")
            if not content:
                continue
            url = passage.get("url")
            score = passage.get("score")
            tokens = self.tokenizer_function(content)

            for start in range(0, len(tokens), k):
                chunk_tokens = tokens[start : start + k]
                chunk_text = self.detokenizer_function(chunk_tokens)
                chunks.append(
                    RefragChunk(
                        text=chunk_text,
                        tokens=chunk_tokens,
                        source_url=url,
                        source_score=score,
                    )
                )

        return chunks

    def encode_chunks(self, chunks: List[RefragChunk]) -> List[RefragChunk]:
        """Apply the encoder function to produce chunk embeddings.

        Requires ``encoder_function`` to have been set during construction.

        Args:
            chunks: List of RefragChunk objects (tokens must be populated).

        Returns:
            The same list with ``embedding`` fields populated.

        Raises:
            RuntimeError: If no encoder_function was provided.
        """
        if self.encoder_function is None:
            raise RuntimeError(
                "encoder_function must be provided to encode chunks. "
                "Pass it to the TavilyRefragClient constructor."
            )

        token_lists = [c.tokens for c in chunks]
        embeddings = self.encoder_function(token_lists)

        for chunk, emb in zip(chunks, embeddings):
            chunk.embedding = emb

        return chunks

    def apply_expansion_policy(
        self,
        chunks: List[RefragChunk],
        query: Optional[str] = None,
    ) -> List[RefragChunk]:
        """Run the expansion policy to decide which chunks to expand.

        The policy receives chunk embeddings and an optional query
        embedding and returns a boolean mask.

        Args:
            chunks: Chunks with embeddings already populated.
            query: Optional query text (tokenized and passed to encoder
                   to produce a query embedding when encoder_function
                   is available).

        Returns:
            The same list with ``expand`` flags set.

        Raises:
            ValueError: If any chunk lacks an embedding.
        """
        for c in chunks:
            if c.embedding is None:
                raise ValueError(
                    "All chunks must have embeddings before applying the "
                    "expansion policy. Call encode_chunks first."
                )

        chunk_embeddings = [c.embedding for c in chunks]

        query_embedding = None
        if query is not None and self.encoder_function is not None:
            query_tokens = self.tokenizer_function(query)
            query_embedding = self.encoder_function([query_tokens])[0]

        expand_mask = self.expansion_policy(chunk_embeddings, query_embedding)

        for chunk, should_expand in zip(chunks, expand_mask):
            chunk.expand = should_expand

        return chunks

    def prepare_context(
        self,
        query: str,
        max_results: int = 10,
        encode: bool = True,
        apply_policy: bool = True,
        **search_kwargs,
    ) -> RefragContext:
        """Full pipeline: search -> chunk -> encode -> policy -> RefragContext.

        Args:
            query: The search query.
            max_results: Maximum number of Tavily search results.
            encode: Whether to run the encoder on chunks. Requires
                    encoder_function to be set.
            apply_policy: Whether to run the expansion policy. Only
                          effective when encode=True.
            **search_kwargs: Extra arguments forwarded to TavilyClient.search.

        Returns:
            A RefragContext ready for decoder consumption.
        """
        response = self.tavily.search(
            query, max_results=max_results, **search_kwargs
        )

        passages = response.get("results", [])
        metadata = {
            k: v for k, v in response.items() if k != "results"
        }

        chunks = self.chunk_passages(passages)

        if encode and self.encoder_function is not None:
            self.encode_chunks(chunks)
            if apply_policy:
                self.apply_expansion_policy(chunks, query=query)

        return RefragContext(
            query=query,
            chunks=chunks,
            chunk_size=self.chunk_size,
            metadata=metadata,
        )
