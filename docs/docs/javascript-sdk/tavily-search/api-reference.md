# API Reference

## Client
The `tavily` function is the entry point to interacting with the Tavily API. Kickstart your journey by calling it with your API Key.

Once you do so, you're ready to search the Web in one line of code! All you need is to pass a `string` as a `query` to one of our methods (detailed below) and you'll start searching!

## Methods
* **`search`**(query, options)
  * Performs a Tavily Search query and returns the response as `TavilySearchResponse`.
  * **Additional parameters** can be provided in the `options` argument (detailed below). The additional parameters supported by this method are: `searchDepth`, `topic`, `days`, `maxResults`, `includeDomains`, `excludeDomains`, `includeAnswer`, `includeRawContent`, `includeImages`, `includeImageDescriptions`. 
  * **Returns** a `TavilySearchResponse`. The details of the exact response format are given in the Search Responses section further down.
  
* **`searchContext`**(query, options)
  * Performs a Tavily Search query and returns a `string` of content and sources within the provided token limit. It's useful for getting only related content from retrieved websites without having to deal with context extraction and token management.
  * The **core parameter** for this function is `maxTokens`, a `number`. It defaults to `4000`. It is provided in the `options` argument (detailed below).
  * **Additional parameters** can be provided in the `options` argument (detailed below). The additional parameters supported by this method are: `searchDepth`, `topic`, `days`, `maxResults`, `includeDomains`, `excludeDomains`.
  * **Returns** a `string` containing the content and sources of the results.

* **`searchQNA`**(query, options)
  * Performs a search and returns a `string` containing an answer to the original query. This is optimal to be used as a tool for AI agents.
  * **Additional parameters** can be provided in the `options` argument (detailed below). The additional parameters supported by this method are: `searchDepth` (defaults to `"advanced"`), `topic`, `days`, `maxResults`, `includeDomains`, `excludeDomains`. 
  * **Returns** a `string` containing a short answer to the search query.

## Options

* **`searchDepth`: string** - The depth of the search. It can be `"basic"` or `"advanced"`. Default is `"basic"` unless specified otherwise in a given method.

* **`topic`: string** - The category of the search. This will determine which of our agents will be used for the search. Currently, only `"general"` and `"news"` are supported. Default is `"general"`.

* **`days`: number (optional)** - The number of days back from the current date to include in the search results. This specifies the time frame of data to be retrieved. Please note that this feature is only available when using the `"news"` search `topic`. Default is `3`.

* **`maxResults`: number** -  The maximum number of search results to return. Default is `5`.

* **`includeImages`: boolean** -  Include a list of query-related images in the response. Default is `False`.

* **`includeImageDescriptions`: bool** - When `includeImages` is set to `true`, this option adds descriptive text for each image.  Default is `false`.

* **`includeAnswer`: boolean** -  Include a short answer to original query. Default is `false`.

* **`includeRawContent`: boolean** -  Include the cleaned and parsed HTML content of each search result. Default is `false`.

* **`includeDomains`: Arraystring** -  A list of domains to specifically include in the search results. Default is `undefined`, which includes all domains. 

* **`excludeDomains`: Arraystring** -  A list of domains to specifically exclude from the search results. Default is `undefined`, which doesn't exclude any domains. 

## Search Responses - `TavilySearchResponse`

* **`answer`: string**- The answer to your search query. This will be `undefined` unless `includeAnswer` is set to `true`.

* **`query`: string** - Your search query.

* **`responseTime`: number** - Your search result response time.

* **`images`: ArrayTavilyImage** - A list of query-related image URLs (and descriptions if requested). Each `TavilyImage` consists of a `url` (`string`) and a `description` (`string`). If `includeImageDescriptions` is not set to `true`, the `description` will be `undefined`.

* **`results`: ArrayTavilySearchResult** - A list of sorted search results ranked by relevancy. Each `TavilySearchResult` is in the following format:
  - **`title`: string** - The title of the search result URL.
  - **`url`: string** - The URL of the search result.
  - **`content`: string** - The most query related content from the scraped URL. We use proprietary AI and algorithms to extract only the most relevant content from each URL, to optimize for context quality and size.
  - **`rawContent`: string** - The parsed and cleaned HTML of the site. For now includes parsed text only. Please note that this will be `undefined` unless `includeRawContent` is set to `true`.
  - **`score`: number** - The relevance score of the search result.
  - **`publishedDate`: string (optional)** - The publication date of the source. This is only available if you are using `"news"` as your search `topic`.


When you send a search query, the response you receive will be in the following format:

```javascript
response = {
  query: "The query provided in the request",
  answer: "A short answer to the query",  // This will be None if includeAnswer is set to False in the request
  images: [ 
    {
      url: "Image 1 URL",
      description: "Image 1 Description",  
    },
    {
      url: "Image 2 URL",
      description: "Image 2 Description",
    },
    {
      url: "Image 3 URL",
      description: "Image 3 Description",
    },
    {
      url: "Image 4 URL",
      description: "Image 4 Description",
    },
    {
      url: "Image 5 URL",
      description: "Image 5 Description",
    }
  ], // The description field will be undefined if includeImageDescriptions is not set to true.
  results: [
    {
      title: "Source 1 Title",
      url: "Source 1 URL",
      content: "Source 1 Content",
      score: 0.99  // This is the "relevancy" score of the source. It ranges from 0 to 1.
    },
    {
      title: "Source 2 Title",
      url: "Source 2 URL",
      content: "Source 2 Content",
      score: 0.97
    }
  ],  // This list will have maxResults elements
  "responseTime": 1.09 // This will be your search response time
}
```