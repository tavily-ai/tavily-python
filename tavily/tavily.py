import requests
import json
import warnings
from .utils import get_max_items_from_list

class TavilyClient:
    def __init__(self, api_key):
        self.base_url = "https://api.tavily.com/search"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
        }

    def _search(self, query, search_depth="basic", topic="general", max_results=5,
                include_domains=None, exclude_domains=None,
                include_answer=False, include_raw_content=False, include_images=False,
                use_cache=True):
        """
        Internal search method to send the request to the API.
        """
        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains or None,
            "exclude_domains": exclude_domains or None,
            "include_images": include_images,
            "api_key": self.api_key,
            "use_cache": use_cache,
        }
        response = requests.post(self.base_url, data=json.dumps(data), headers=self.headers, timeout=100)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code

    def search(self, query, search_depth="basic", **kwargs):
        """
        Combined search method. Set search_depth to either "basic" or "advanced".
        """
        return self._search(query, search_depth=search_depth, **kwargs)

    def get_search_context(self, query, search_depth="basic", max_tokens=4000, **kwargs):
        """
        Get the search context for a query. Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        max_tokens: The maximum number of tokens to return (based on openai token compute). Defaults to 4000.

        Returns a string of JSON containing the search context up to context limit.
        """
        search_result = self._search(query, search_depth, **kwargs)
        sources = search_result.get("results", [])
        context = [{"url": obj["url"], "content": obj["content"]} for obj in sources]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    def qna_search(self, query, search_depth="advanced", **kwargs):
        """
        Q&A search method. Search depth is advanced by default to get the best answer.
        """
        search_result = self._search(query, search_depth=search_depth, include_answer=True, **kwargs)
        return search_result.get("answer", "")

class Client(TavilyClient):
    def __init__(self, *args, **kwargs):
        warnings.warn("Client is deprecated, please use TavilyClient instead", DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)
