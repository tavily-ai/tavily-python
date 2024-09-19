# API Reference

## Client

The `TavilyClient` class is the entry point to interacting with the Tavily API. Kickstart your journey by instantiating it with your API key. Once you do so, you're ready to search the Web in one line of code! All you need is to pass a `str` as a `query` to one of our methods (detailed below) and you'll start searching!

### Asynchronous Client
If you want to use Tavily asynchronously, you will need to instantiate an `AsyncTavilyClient` instead. The asynchronous client's interface is identical to the synchronous client's, the only difference being that all methods are asynchronous.

## Methods
* **`search`**(query, **kwargs)
  * Performs a Tavily Search query and returns the response as a well-structured `dict`.
  * **Additional parameters** can be provided as keyword arguments (detailed below). The keyword arguments supported by this method are: `search_depth`, `topic`, `days`,`max_results`, `include_domains`, `exclude_domains`, `include_answer`, `include_raw_content`, `include_images`, `include_image_descriptions`. 
  * **Returns** a `dict` with all related response fields. If you decide to use the asynchronous client, returns a `coroutine` resolving to that `dict`. The details of the exact response format are given in the [Search Responses](#search-responses) section.
  
* **`get_search_context`**(query, **kwargs)
  * Performs a Tavily Search query and returns a `str` of content and sources within the provided token limit. It's useful for getting only related content from retrieved websites without having to deal with context extraction and token management.
  * The **core parameter** for this function is `max_tokens`, an `int`. It defaults to `4000`. It is provided as a keyword argument.
  * **Additional parameters** can be provided as keyword arguments (detailed below). The keyword arguments supported by this method are: `search_depth`, `topic`, `days`, `max_results`, `include_domains`, `exclude_domains`.
  * **Returns** a `str` containing the content and sources of the results. If you decide to use the asynchronous client, returns a `coroutine` resolving to that `str`.

* **`qna_search`**(query, **kwargs)
  * Performs a search and returns a `str` containing an answer to the original query. This is optimal to be used as a tool for AI agents.
  * **Additional parameters** can be provided as keyword arguments (detailed below). The keyword arguments supported by this method are: `search_depth` (defaults to `"advanced"`), `topic`, `days`, `max_results`, `include_domains`, `exclude_domains`. 
  * **Returns** a `str` containing a short answer to the search query. If you decide to use the asynchronous client, returns a `coroutine` resolving to that `str`.

### Keyword Arguments (optional)

* **`search_depth`: str** - The depth of the search. It can be `"basic"` or `"advanced"`. Default is `"basic"` unless specified otherwise in a given method.

* **`topic`: str** - The category of the search. This will determine which of our agents will be used for the search. Currently, only `"general"` and `"news"` are supported. Default is `"general"`.

* **`days`: int (optional)** - The number of days back from the current date to include in the search results. This specifies the time frame of data to be retrieved. Please note that this feature is only available when using the `"news"` search `topic`. Default is `3`.

* **`max_results`: int** -  The maximum number of search results to return. Default is `5`.

* **`include_images`: bool** -  Include a list of query-related images in the response. Default is `False`.

* **`include_image_descriptions`: bool** - Include a list of query-related images and their descriptions in the response. Default is `False`.

* **`include_answer`: bool** -  Include a short answer to original query. Default is `False`.

* **`include_raw_content`: bool** -  Include the cleaned and parsed HTML content of each search result. Default is `False`.

* **`include_domains`: list[str]** -  A list of domains to specifically include in the search results. Default is `None`, which includes all domains. 

* **`exclude_domains`: list[str]** -  A list of domains to specifically exclude from the search results. Default is `None`, which doesn't exclude any domains. 

### Search Responses

* **`answer`: str**- The answer to your search query. This will be `None` unless `include_answer` is set to `True`.

* **`query`: str** - Your search query.

* **`response_time`: float** - Your search result response time.

* **`images`: list[str | dict]** - A list of query-related image URLs.  If `include_image_descriptions` is set to `True` each entry will be a dictionary with `url` and `description`

* **`results`: list** - A list of sorted search results ranked by relevancy. Each result is in the following format:
  - **`title`: str** - The title of the search result URL.
  - **`url`: str** - The URL of the search result.
  - **`content`: str** - The most query related content from the scraped URL. We use proprietary AI and algorithms to extract only the most relevant content from each URL, to optimize for context quality and size.
  - **`raw_content`: str** - The parsed and cleaned HTML of the site. For now includes parsed text only. Please note that this will be `None` unless `include_raw_content` is set to `True`.
  - **`score`: float** - The relevance score of the search result.
  - **`published_date`: str (optional)** - The publication date of the source. This is only available if you are using `"news"` as your search `topic`.


When you send a search query, the response `dict` you receive will be in the following format:

```python
response = {
  "query": "The query provided in the request",
  "answer": "A short answer to the query",  # This will be None if include_answer is set to False in the request
  "follow_up_questions": None,  # This feature is still in development
  "images": [ 
    {
      "url": "Image 1 URL",
      "description": "Image 1 Description",  
    },
    {
      "url": "Image 2 URL",
      "description": "Image 2 Description",
    },
    {
      "url": "Image 3 URL",
      "description": "Image 3 Description",
    },
    {
      "url": "Image 4 URL",
      "description": "Image 4 Description",
    },
    {
      "url": "Image 5 URL",
      "description": "Image 5 Description",
    }
  ],  # This will be a list of string URLs if `include_images` is True and `include_image_descriptions` is False, or an empty list if both set to False.
  "results": [
    {
      "title": "Source 1 Title",
      "url": "Source 1 URL",
      "content": "Source 1 Content",
      "score": 0.99  # This is the "relevancy" score of the source. It ranges from 0 to 1.
    },
    {
      "title": "Source 2 Title",
      "url": "Source 2 URL",
      "content": "Source 2 Content",
      "score": 0.97
    }
  ],  # This list will have max_results elements
  "response_time": 1.09 # This will be your search response time
}
```



## ⚠️ Error Handling 

The Tavily Python SDK includes comprehensive error handling to ensure smooth interaction with the API. Below are the specific exceptions that might be raised during usage:

1. **Missing API Key**: If no API key is provided when initializing the `TavilyClient`, a `tavily.MissingAPIKeyError` will be raised. Ensure you pass a valid API key to the `TavilyClient` during instantiation.
   
   ```python
   from tavily import TavilyClient, MissingAPIKeyError

   try:
       tavily_client = TavilyClient(api_key="")
   except MissingAPIKeyError:
       print("API key is missing. Please provide a valid API key.")
   ```

2. **Invalid API Key**: If the API key provided is invalid, a `tavily.InvalidAPIKeyError` will be raised when sending a search query. Double-check that your API key is correct and active.

   ```python
   from tavily import TavilyClient, InvalidAPIKeyError

   tavily_client = TavilyClient(api_key="invalid-api-key")

   try:
       response = tavily_client.search("Who is Leo Messi?")
   except InvalidAPIKeyError:
       print("Invalid API key provided. Please check your API key.")
   ```

3. **Usage Limit Exceeded**: If the API key provided is valid but the request fails due to exceeding the rate limit, surpassing the plan's monthly limit, or hitting the key's pre-set monthly limit, a `tavily.UsageLimitExceededError` will be raised. Consider upgrading your plan or checking your usage limits.

   ```python
   from tavily import TavilyClient, UsageLimitExceededError

   tavily_client = TavilyClient(api_key="valid-api-key")

   try:
       response = tavily_client.search("Who is Leo Messi?")
   except UsageLimitExceededError:
       print("Usage limit exceeded. Please check your plan's usage limits or consider upgrading.")
   ```

These errors ensure that you are aware of the specific issues related to your API key usage, allowing you to take appropriate actions to resolve them.