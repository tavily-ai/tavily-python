# API Reference

## Client

The `TavilyHybridClient` class is your gateway to Tavily Hybrid RAG. There are a few important parameters to keep in mind when you are instantiating a Tavily Hybrid Client.

### Constructor parameters
* **`api_key`: str** - Your Tavily API Key

* **`db_provider`: str** - Your database provider. Currently, only `"mongodb"` is supported.

* **`collection`: Collection** - A reference to the MongoDB collection that will be used for local search.

* **`index`: str** - The name of the vector index to be used for vector search on the specified `collection`.

* **`embeddings_field`: str (optional)** - The name of the field that stores the embeddings in the specified collection. This field MUST be the same one used in the specified index. This will also be used when inserting web search results in the database using our default function. Default is `"embeddings"`.

* **`content_field`: str (optional)** - The name of the field that stores the text content in the specified collection. This will also be used when inserting web search results in the database using our default function. Default is `"content"`.

* **`embedding_function`: function (optional)** - A custom embedding function (if you want to use one). The function must take in a `list[str]` corresponding to the list of strings to be embedded, as well as an additional string defining the type of document. It must return a `list[list[float]]`, one embedding per input string. If no function is provided, defaults to Cohere's Embed. Keep in mind that you shouldn't mix different embeddings in the same database collection.

* **`ranking_function`: function (optional)** - A custom ranking function (if you want to use one). If no function is provided, defaults to Cohere's Rerank. It should return an ordered `list[dict]` where the documents are sorted by decreasing relevancy to your query. Each returned document will have two properties - `content`, which is a `str`, and `score`, which is a `float`. The fuction MUST accept the following parameters:
  * **`query`: str** - This is the query you are executing. When your ranking function is called during Hybrid RAG, the `query` parameter of your `search` call (more details below) will be passed as `query`.
  * **`documents` list[dict]: ** - This is the list of documents that are returned by your Hybrid RAG call and that you want to sort. Each document will have two properties - `content`, which is a `str`, and `score`, which is a `float`.
  * **`top_n`: int** - This is the number of results you want to return after ranking. When your ranking function is called during Hybrid RAG, the `max_results` value will be passed as `top_n`.

## Methods

* **`search`**(query, max_results=10, max_local=None, max_foreign=None, save_foreign=False, **kwargs)
  * Performs a Tavily Hybrid RAG query and returns the retrieved documents as a `list[dict]` where the documents are sorted by decreasing relevancy to your query. Each returned document will have three properties - `content` (`str`), `score` (`float`), and `origin`, which is either `local` or `foreign`.
  * **Core Parameters**
    * **`query`: str** - The query you want to search for.
    * **`max_results`: int** - The maximum number of total search results to return. Default is `10`.
    * **`max_local`: int** - The maximum number of local search results to return. Default is `None`, which defaults to `max_results`.
    * **`max_foreign`: int** - The maximum number of web search results to return. Default is `None`, which defaults to `max_results`.
    * **`save_foreign`: Union[bool, function]** - Save documents from the web search in the local database. If `True` is passed, our default saving function (which only saves the content `str` and the embedding `list[float]` will be used.) If `False` is passed, no web search result documents will be saved in the local database. If a function is passed, that function MUST take in a `dict` as a parameter, and return another `dict`. The input `dict` contains all properties of the returned Tavily result object. The output dict is the final document that will be inserted in the database. You are free to add to it any fields that are supported by the database, as well as remove any of the default ones. **If this function returns `None`, the document will not be saved in the database.**

  * **Additional parameters** can be provided as keyword arguments (detailed below). The keyword arguments supported by this method are: `search_depth`, `topic`, `include_raw_content`, `include_domains`, `exclude_domains`. Refer to the [Tavily Search API Reference](/docs/python-sdk/tavily-search/api-reference#keyword-arguments-optional) for more information on these parameters.