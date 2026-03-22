# REFRAG Preprocessing Example
#
# This example shows how to use TavilyRefragClient to retrieve web passages
# via Tavily, chunk them into k-token blocks, encode them with a pluggable
# encoder, and apply an expansion policy -- producing a RefragContext that
# is ready to be fed into a REFRAG-compatible decoder.
#
# Replace the dummy encoder and policy below with your own REFRAG-trained
# models (e.g. RoBERTa encoder + RL expansion policy from the REFRAG paper).

import os
import math
from tavily import TavilyRefragClient


# -- Pluggable encoder -------------------------------------------------------
# In a real setup, this would call a lightweight encoder like RoBERTa to
# produce chunk embeddings.  Here we use a trivial placeholder.

def my_encoder(token_lists):
    """Encode each token chunk into a fixed-size embedding vector."""
    embeddings = []
    for tokens in token_lists:
        dim = 8
        emb = [float(t % 100) / 100.0 for t in tokens[:dim]]
        emb += [0.0] * (dim - len(emb))
        embeddings.append(emb)
    return embeddings


# -- Pluggable expansion policy -----------------------------------------------
# In a real setup, this would be an RL-trained policy that decides which
# chunks need full token-level attention in the decoder.  Here we expand
# chunks whose embedding norm exceeds a threshold.

def my_expansion_policy(chunk_embeddings, query_embedding=None):
    """Expand chunks whose L2 norm is above the median (heuristic demo)."""
    norms = [math.sqrt(sum(x * x for x in emb)) for emb in chunk_embeddings]
    if not norms:
        return []
    threshold = sorted(norms)[len(norms) // 2]
    return [n > threshold for n in norms]


# -- Build the client ---------------------------------------------------------

client = TavilyRefragClient(
    api_key=os.environ["TAVILY_API_KEY"],
    chunk_size=16,                        # k=16 as in the paper
    encoder_function=my_encoder,
    expansion_policy=my_expansion_policy,
)


# -- Option 1: Full pipeline in one call --------------------------------------

ctx = client.prepare_context(
    query="What are the latest advances in retrieval augmented generation?",
    max_results=5,
    search_depth="advanced",
)

print(f"Query: {ctx.query}")
print(f"Total chunks: {len(ctx.chunks)}")
print(f"Compressed (feed as embeddings): {len(ctx.compressed_chunks)}")
print(f"Expanded  (feed as full tokens): {len(ctx.expanded_chunks)}")
print(f"Metadata: {ctx.metadata}")

for i, chunk in enumerate(ctx.chunks[:5]):
    status = "EXPAND" if chunk.expand else "COMPRESS"
    print(f"  [{status}] chunk {i}: {chunk.text[:60]}...")


# -- Option 2: Step-by-step (useful when you already have passages) -----------

response = client.tavily.search("REFRAG paper Meta 2025", max_results=3)
passages = response["results"]

chunks = client.chunk_passages(passages, chunk_size=8)
chunks = client.encode_chunks(chunks)
chunks = client.apply_expansion_policy(chunks, query="REFRAG paper Meta 2025")

print(f"\nStep-by-step: {len(chunks)} chunks from {len(passages)} passages")
for c in chunks[:3]:
    print(f"  expand={c.expand}  url={c.source_url}  tokens={len(c.tokens)}")
