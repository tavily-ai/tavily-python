# Examples

## Setup
Follow the setup instructions in [Getting Started](/docs/python-sdk/tavily-hybrid-rag)

## Samples

### Sample 1: Using a custom saving function
You might want to add some extra properties to documents you're inserting or even discard some of them based on custom criteria. This can be done by passing a function to the `save_foreign` parameter:
```python
def my_saving_function(document):
    if document['domain'] != 'wikipedia.org':
        return None # Do not save this document
    
    return {
        'content': document['content'],

         # Rename title field
        'site_title': document['title'],

        # Add new field
        'added_at': datetime.now()
    }

results = hybrid_search.search("Who is Leo Messi?", save_foreign=my_saving_function)
```

### Sample 2: Using a custom embedding function
By default, we use [Cohere](https://cohere.com/embeddings) for our embeddings. If you want to use your own embeddings, can pass a custom embedding function to the TavilyHybridClient:
```python
def my_embedding_function(text):
    return my_embedding_model.encode(text)

hybrid_search = TavilyHybridClient(
    # ...
    embedding_function=my_embedding_function
)
```

### Sample 3: Using a custom ranking function
Cohere's [rerank](https://cohere.com/rerank) model is used by default, but you can pass your own function to the `ranking_function` parameter:
```python
def my_ranking_function(query, documents, top_n):
    return my_ranking_model.rank(query, documents, top_n)

hybrid_search = TavilyHybridClient(
    # ...
    ranking_function=my_ranking_function
)
```