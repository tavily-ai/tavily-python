# Examples

## Setup
Follow the setup instructions in [Getting Started](/docs/python-sdk/tavily-hybrid-rag/getting-started)

## Samples

### Sample 1: Using a custom saving function
You might want to add some extra properties to documents you're inserting or even discard some of them based on custom criteria. This can be done by passing a function to the `save_foreign` parameter:
```python
def save_document(document):
    if document['score'] < 0.5:
        return None # Do not save documents with low scores
    
    return {
        'content': document['content'],

         # Save the title and URL in the database
        'site_title': document['title'],
        'site_url': document['url'],

        # Add a new field
        'added_at': datetime.now()
    }

results = hybrid_rag.search("Who is Leo Messi?", save_foreign=save_document)
```

### Sample 2: Using a custom embedding function
By default, we use [Cohere](https://cohere.com/embeddings) for our embeddings. If you want to use your own embeddings, can pass a custom embedding function to the TavilyHybridClient:
```python
def my_embedding_function(text):
    return my_embedding_model.encode(text)

hybrid_rag = TavilyHybridClient(
    # ...
    embedding_function=my_embedding_function
)
```

### Sample 3: Using a custom ranking function
Cohere's [rerank](https://cohere.com/rerank) model is used by default, but you can pass your own function to the `ranking_function` parameter:
```python
def my_ranking_function(query, documents, top_n):
    return my_ranking_model.rank(query, documents, top_n)

hybrid_rag = TavilyHybridClient(
    # ...
    ranking_function=my_ranking_function
)
```