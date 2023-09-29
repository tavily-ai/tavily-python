import requests
import json

class Client:
    def __init__(self, api_key):
        self.base_url = "https://api.tavily.com/search"
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            # any other headers you want
        }

    def _search(self, query, search_depth="basic", max_results=10,
                include_domains=None, exclude_domains=None,
                include_answer=False, include_raw_content=False, include_images=False):
        """
        Internal search method to send the request to the API.
        """
        data = {
            "query": query,
            "search_depth": search_depth,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains or [],
            "exclude_domains": exclude_domains or [],
            "include_images": include_images,
            "api_key": self.api_key
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
