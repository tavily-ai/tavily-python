import requests
import json
import warnings
import os
from typing import Literal, Sequence, Optional, List, Union
from concurrent.futures import ThreadPoolExecutor, as_completed
from .utils import get_max_items_from_list
from .errors import UsageLimitExceededError, InvalidAPIKeyError, MissingAPIKeyError, BadRequestError, ForbiddenError


class TavilyClient:
    """
    Tavily API client class.
    """

    def __init__(self, api_key: Optional[str] = None, proxies: Optional[dict[str, str]] = None):
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise MissingAPIKeyError()

        resolved_proxies = {
            "http": proxies.get("http") if proxies else os.getenv("TAVILY_HTTP_PROXY"),
            "https": proxies.get("https") if proxies else os.getenv("TAVILY_HTTPS_PROXY"),
        }

        resolved_proxies = {k: v for k, v in resolved_proxies.items() if v} or None

        self.base_url = "https://api.tavily.com"
        self.api_key = api_key
        self.proxies = resolved_proxies
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _search(self,
                query: str,
                search_depth: Literal["basic", "advanced"] = "basic",
                topic: Literal["general", "news", "finance"] = "general",
                time_range: Literal["day", "week", "month", "year"] = None,
                days: int = 7,
                max_results: int = 5,
                include_domains: Sequence[str] = None,
                exclude_domains: Sequence[str] = None,
                include_answer: Union[bool, Literal["basic", "advanced"]] = False,
                include_raw_content: bool = False,
                include_images: bool = False,
                timeout: int = 60,
                **kwargs
                ) -> dict:
        """
        Internal search method to send the request to the API.
        """

        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "time_range": time_range,
            "days": days,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_images": include_images,
        }

        if kwargs:
            data.update(kwargs)

        timeout = min(timeout, 120)

        response = requests.post(self.base_url + "/search", data=json.dumps(data), headers=self.headers, timeout=timeout, proxies=self.proxies)

        if response.status_code == 200:
            return response.json()
        else:
            detail = ""
            try:
                detail = response.json().get("detail", {}).get("error", None)
            except Exception:
                pass

            if response.status_code == 429:
                raise UsageLimitExceededError(detail)
            elif response.status_code in [403,432,433]:
                raise ForbiddenError(detail)
            elif response.status_code == 401:
                raise InvalidAPIKeyError(detail)
            elif response.status_code == 400:
                raise BadRequestError(detail)
            else:
                raise response.raise_for_status()


    def search(self,
               query: str,
               search_depth: Literal["basic", "advanced"] = "basic",
               topic: Literal["general", "news", "finance" ] = "general",
               time_range: Literal["day", "week", "month", "year"] = None,
               days: int = 7,
               max_results: int = 5,
               include_domains: Sequence[str] = None,
               exclude_domains: Sequence[str] = None,
               include_answer: Union[bool, Literal["basic", "advanced"]] = False,
               include_raw_content: bool = False,
               include_images: bool = False,
               timeout: int = 60,
               **kwargs,  # Accept custom arguments
               ) -> dict:
        """
        Combined search method.
        """
        timeout = min(timeout, 120)
        response_dict = self._search(query,
                                     search_depth=search_depth,
                                     topic=topic,
                                     time_range=time_range,
                                     days=days,
                                     max_results=max_results,
                                     include_domains=include_domains,
                                     exclude_domains=exclude_domains,
                                     include_answer=include_answer,
                                     include_raw_content=include_raw_content,
                                     include_images=include_images,
                                     timeout=timeout,
                                     **kwargs,
                                     )

        tavily_results = response_dict.get("results", [])

        response_dict["results"] = tavily_results

        return response_dict

    def _extract(self,
                 urls: Union[List[str], str],
                 include_images: bool = False,
                 extract_depth: Literal["basic", "advanced"] = "basic",
                 timeout: int = 60,
                 **kwargs
                 ) -> dict:
        """
        Internal extract method to send the request to the API.
        """
        data = {
            "urls": urls,
            "include_images": include_images,
            "extract_depth": extract_depth,
        }
        if kwargs:
            data.update(kwargs)

        timeout = min(timeout, 120)

        response = requests.post(self.base_url + "/extract", data=json.dumps(data), headers=self.headers, timeout=timeout, proxies=self.proxies)

        if response.status_code == 200:
            return response.json()
        else:
            detail = ""
            try:
                detail = response.json().get("detail", {}).get("error", None)
            except Exception:
                pass

            if response.status_code == 429:
                raise UsageLimitExceededError(detail)
            elif response.status_code in [403,432,433]:
                raise ForbiddenError(detail)
            elif response.status_code == 401:
                raise InvalidAPIKeyError(detail)
            elif response.status_code == 400:
                raise BadRequestError(detail)
            else:
                raise response.raise_for_status()

    def extract(self,
                urls: Union[List[str], str],  # Accept a list of URLs or a single URL
                include_images: bool = False,
                extract_depth: Literal["basic", "advanced"] = "basic",
                timeout: int = 60,
                **kwargs,  # Accept custom arguments
                ) -> dict:
        """
        Combined extract method.
        """
        timeout = min(timeout, 120)
        response_dict = self._extract(urls,
                                      include_images,
                                      extract_depth,
                                      timeout,
                                      **kwargs)

        tavily_results = response_dict.get("results", [])
        failed_results = response_dict.get("failed_results", [])

        response_dict["results"] = tavily_results
        response_dict["failed_results"] = failed_results

        return response_dict

    def get_search_context(self,
                           query: str,
                           search_depth: Literal["basic", "advanced"] = "basic",
                           topic: Literal["general", "news", "finance"] = "general",
                           days: int = 7,
                           max_results: int = 5,
                           include_domains: Sequence[str] = None,
                           exclude_domains: Sequence[str] = None,
                           max_tokens: int = 4000,
                           timeout: int = 60,
                           **kwargs,  # Accept custom arguments
                           ) -> str:
        """
        Get the search context for a query. Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        max_tokens: The maximum number of tokens to return (based on openai token compute). Defaults to 4000.

        Returns a string of JSON containing the search context up to context limit.
        """
        timeout = min(timeout, 120)
        response_dict = self._search(query,
                                     search_depth=search_depth,
                                     topic=topic,
                                     days=days,
                                     max_results=max_results,
                                     include_domains=include_domains,
                                     exclude_domains=exclude_domains,
                                     include_answer=False,
                                     include_raw_content=False,
                                     include_images=False,
                                     timeout=timeout,
                                     **kwargs,
                                     )
        sources = response_dict.get("results", [])
        context = [{"url": source["url"], "content": source["content"]} for source in sources]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    def qna_search(self,
                   query: str,
                   search_depth: Literal["basic", "advanced"] = "advanced",
                   topic: Literal["general", "news", "finance"] = "general",
                   days: int = 7,
                   max_results: int = 5,
                   include_domains: Sequence[str] = None,
                   exclude_domains: Sequence[str] = None,
                   timeout: int = 60,
                   **kwargs,  # Accept custom arguments
                   ) -> str:
        """
        Q&A search method. Search depth is advanced by default to get the best answer.
        """
        timeout = min(timeout, 120)
        response_dict = self._search(query,
                                     search_depth=search_depth,
                                     topic=topic,
                                     days=days,
                                     max_results=max_results,
                                     include_domains=include_domains,
                                     exclude_domains=exclude_domains,
                                     include_raw_content=False,
                                     include_images=False,
                                     include_answer=True,
                                     timeout=timeout,
                                     **kwargs,
                                     )
        return response_dict.get("answer", "")

    def get_company_info(self,
                         query: str,
                         search_depth: Literal["basic", "advanced"] = "advanced",
                         max_results: int = 5,
                         timeout: int = 60,
                         ) -> Sequence[dict]:
        """ Company information search method. Search depth is advanced by default to get the best answer. """
        timeout = min(timeout, 120)
        def _perform_search(topic):
            return self._search(query,
                                search_depth=search_depth,
                                topic=topic,
                                max_results=max_results,
                                include_answer=False,
                                timeout=timeout)

        with ThreadPoolExecutor() as executor:
            # Initiate the search for each topic in parallel
            future_to_topic = {executor.submit(_perform_search, topic): topic for topic in
                               ["news", "general", "finance"]}

            all_results = []

            # Process the results as they become available
            for future in as_completed(future_to_topic):
                data = future.result()
                if 'results' in data:
                    all_results.extend(data['results'])

        # Sort all the results by score in descending order and take the top 'max_results' items
        sorted_results = sorted(all_results, key=lambda x: x['score'], reverse=True)[:max_results]

        return sorted_results


class Client(TavilyClient):
    """
    Tavily API client class.

    WARNING! This class is deprecated. Please use TavilyClient instead.
    """

    def __init__(self, kwargs):
        warnings.warn("Client is deprecated, please use TavilyClient instead", DeprecationWarning, stacklevel=2)
        super().__init__(kwargs)
