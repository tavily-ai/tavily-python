# API Reference

## Client

The `TavilyHybridClient` class is your gateway to Tavily Hybrid RAG. There are a few important parameters to keep in mind when you are instantiating a Tavily Hybrid Client.

### Constructor parameters
* **`api_key`: str** - Your Tavily API Key

* **`db_provider`: str** - Your database provider. Currently, only `"mongodb"` is supported. Default is `"mongodb"`.

* **`collection`: str** - The name of the collection you want to perform vector search on (for local data).

* **`index`: str** - The name of the vector index to be used for vector search on the specified `collection`.

* **`embeddings_field`: str (optional)** - The name of the field that stores the embeddings in the specified collection. This field MUST be the same one used in the specified index. This will also be used when inserting web search results in the database using our default function. Default is `"embeddings"`.

* **`content_field`: str (optional)** - The name of the field that stores the text content in the specified collection. This will also be used when inserting web search results in the database using our default function. Default is `"content"`.

* **`embedding_function`: function (optional)** - A custom embedding function (if you want to use one). The function MUST take in a `str` and return a `list[float]`. If no function is provided, defaults to Cohere's Embed. Keep in mind that you shouldn't mix different embeddings in the same database collection.

* **`ranking_function`: function (optional)** - A custom ranking function (if you want to use one). If no function is provided, defaults to Cohere's Rerank. It should return an ordered `list[dict]` where the documents are sorted by decreasing relevancy to your query. Each returned document will have two properties - `content`, which is a `str`, and `score`, which is a `float`. The fuction MUST accept the following parameters:
  * **`query`: str** - This is the query you are executing. When your ranking function is called during Hybrid RAG, the `query` parameter of your `search` call (more details below) will be passed as `query`.
  * **`documents` list[dict]: ** - This is the list of documents that are returned by your Hybrid RAG call and that you want to sort. Each document will have two properties - `content`, which is a `str`, and `score`, which is a `float`.
  * **`top_n`: int** - This is the number of results you want to return after ranking. When your ranking function is called during Hybrid RAG, the `max_results` value will be passed as `top_n`.

## Methods

* **`search`**(query, **kwargs)
  * Performs a Tavily Hybrid RAG query and returns the retrieved documents as a `list[dict]` where the documents are sorted by decreasing relevancy to your query. Each returned document will have two properties - `content`, which is a `str`, and `score`, which is a `float`.
  * **Additional parameters** can be provided as keyword arguments (detailed below). The keyword arguments supported by this method are: `search_depth`, `topic`, `max_results`, `max_local`, `max_foreign`, `save_foreign`, `include_domains`, `exclude_domains`, `use_cache`.

### Keyword Arguments (optional)

* **`search_depth`: str** - The depth of the web search. It can be `"basic"` or `"advanced"`. Default is `"basic"` unless specified otherwise in a given method.

* **`topic`: str** - The category of the web search. This will determine which of our agents will be used for the search. Currently, only `"general"` and `"news"` are supported. Default is `"general"`.

* **`max_results`: int** -  The maximum number of total search results to return. Default is `10`.

* **`max_foreign`: int** -  The maximum number of total search results to return. Default is `None`, which defaults to `max_results`.

* **`max_local`: int** -  The maximum number of total search results to return. Default is `None`, which defaults to `max_results`.

* **`include_domains`: list[str]** -  A list of domains to specifically include in the search results. Default is `None`, which includes all domains. Please note that this feature is only available when using the `"general"` search `topic`.

* **`exclude_domains`: list[str]** -  A list of domains to specifically exclude from the search results. Default is `None`, which doesn't exclude any domains. Please note that this feature is only available when using the `"general"` search `topic`.

* **`use_cache`: bool** - Use the cached web search results. Default is `True`. If `False` is passed, a new web search will be done before generating your search results.

* **`save_foreign`: Union[bool, function]** - Save documents from the web search in the local database. If `True` is passed, our default saving function (which only saves the content `str` and the embedding `list[float]` will be used.) If `False` is passed, no web search result documents will be saved in the local database. If a function is passed, that function MUST take in a `dict` as a parameter, and return another `dict`. The input `dict` will represent a document, and will have two properties - `content`, which is a `str`, and `embedding`, which is a `list[float]`. The output dict is the final document that will be inserted in the database. You are free to add to it any fields that are supported by the database, as well as remove any of the default ones.