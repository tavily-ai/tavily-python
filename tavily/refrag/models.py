from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class RefragChunk:
    """A single k-token chunk of a retrieved passage, following the REFRAG paper's
    chunk representation (Section 2: C_i = {x_{q+k*i}, ..., x_{q+k*i+k-1}}).

    Attributes:
        text: Raw text of the chunk before tokenization.
        tokens: Token IDs produced by the tokenizer.
        embedding: Chunk embedding from the encoder (None until encode_chunks is called).
        expand: Whether the expansion policy selected this chunk for full-token decoding.
        source_url: Origin URL from the Tavily search result.
        source_score: Relevance score from the Tavily search result.
    """
    text: str
    tokens: List[int]
    embedding: Optional[List[float]] = None
    expand: bool = False
    source_url: Optional[str] = None
    source_score: Optional[float] = None


@dataclass
class RefragContext:
    """Preprocessed REFRAG-compatible context ready for decoder consumption.

    The decoder receives compressed chunk embeddings for most passages and
    full token embeddings only for chunks flagged by the expansion policy
    (see REFRAG paper, Section 2 & Figure 1).

    Attributes:
        query: Original query text.
        chunks: All processed chunks in passage order.
        chunk_size: The k value (tokens per chunk) used during chunking.
        metadata: Tavily response metadata (response_time, images, etc.).
    """
    query: str
    chunks: List[RefragChunk]
    chunk_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def compressed_chunks(self) -> List[RefragChunk]:
        """Chunks to feed as embeddings (expand=False)."""
        return [c for c in self.chunks if not c.expand]

    @property
    def expanded_chunks(self) -> List[RefragChunk]:
        """Chunks to feed as full tokens (expand=True)."""
        return [c for c in self.chunks if c.expand]
