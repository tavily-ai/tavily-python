"""
Asynchronous Tavily API Client Implementation.

This module provides an asynchronous Python client for interacting with the Tavily API,
offering non-blocking operations for web search, content extraction, web crawling,
and more. The client uses httpx for asynchronous HTTP requests.

The main class `AsyncTavilyClient` provides methods for:
- Asynchronous web search with customizable parameters
- Asynchronous content extraction from URLs
- Asynchronous web crawling with configurable depth and breadth
- Asynchronous site mapping
- Asynchronous question answering
- Asynchronous company information retrieval

Example:
    >>> import asyncio
    >>> async def main():
    ...     client = AsyncTavilyClient(api_key="your-api-key")
    ...     results = await client.search("Python programming")
    ...     print(results)
    >>> asyncio.run(main())
"""

import asyncio
import json
import os
from typing import List, Literal, Optional, Sequence, Union

import httpx

from .config import AllowedCategory
from .errors import (
    BadRequestError,
    ForbiddenError,
    InvalidAPIKeyError,
    MissingAPIKeyError,
    UsageLimitExceededError,
)
from .utils import get_max_items_from_list


class AsyncTavilyClient:
    """
    Async Tavily API client class.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        company_info_tags: Sequence[str] = ("news", "general", "finance"),
        proxies: Optional[dict[str, str]] = None,
    ) -> None:
        """Initialize the asynchronous Tavily client.

        Args:
            api_key (Optional[str]): The Tavily API key. If not provided, will be
                read from the TAVILY_API_KEY environment variable.
            company_info_tags (Sequence[str]): Tags to use for company information
                searches. Defaults to ("news", "general", "finance").
            proxies (Optional[dict[str, str]]): Proxy configuration for requests.
                Can include 'http' and 'https' keys.

        Raises:
            MissingAPIKeyError: If no API key is provided and TAVILY_API_KEY is not set.
        """
        if api_key is None:
            api_key = os.getenv("TAVILY_API_KEY")

        if not api_key:
            raise MissingAPIKeyError()

        proxies = proxies or {}

        mapped_proxies = {
            "http://": proxies.get("http", os.getenv("TAVILY_HTTP_PROXY")),
            "https://": proxies.get("https", os.getenv("TAVILY_HTTPS_PROXY")),
        }

        mapped_proxies = {key: value for key, value in mapped_proxies.items() if value}

        proxy_mounts = (
            {
                scheme: httpx.AsyncHTTPTransport(proxy=proxy)
                for scheme, proxy in mapped_proxies.items()
            }
            if mapped_proxies
            else None
        )

        self._client_creator = lambda: httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            base_url="https://api.tavily.com",
            mounts=proxy_mounts,
        )
        self._company_info_tags = company_info_tags

    async def _search(
        self,
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
        **kwargs,
    ) -> dict:
        """Internal method to perform an asynchronous search request to the Tavily API.

        Args:
            query (str): The search query string.
            search_depth (Literal["basic", "advanced"]): The depth of the search.
                'basic' for quick results, 'advanced' for more comprehensive results.
            topic (Literal["general", "news", "finance"]): The topic category for the search.
            time_range (Optional[Literal["day", "week", "month", "year"]]): Time range for results.
            days (int): Number of days to look back for results.
            max_results (int): Maximum number of results to return.
            include_domains (Optional[Sequence[str]]): List of domains to include in results.
            exclude_domains (Optional[Sequence[str]]): List of domains to exclude from results.
            include_answer (Union[bool, Literal["basic", "advanced"]]): Whether to include an AI-generated answer.
            include_raw_content (bool): Whether to include raw content in results.
            include_images (bool): Whether to include images in results.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: The API response containing search results.

        Raises:
            UsageLimitExceededError: If API usage limit is exceeded.
            ForbiddenError: If the request is forbidden.
            InvalidAPIKeyError: If the API key is invalid.
            BadRequestError: If the request is malformed.
            httpx.HTTPError: For other HTTP errors.
        """
        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "time_range'": time_range,
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

        async with self._client_creator() as client:
            response = await client.post(
                "/search", content=json.dumps(data), timeout=timeout
            )

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
            elif response.status_code in [403, 432, 433]:
                raise ForbiddenError(detail)
            elif response.status_code == 401:
                raise InvalidAPIKeyError(detail)
            elif response.status_code == 400:
                raise BadRequestError(detail)
            else:
                raise response.raise_for_status()

    async def search(
        self,
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
        **kwargs,  # Accept custom arguments
    ) -> dict:
        """Perform an asynchronous search using the Tavily API.

        This method provides a high-level interface for performing asynchronous web
        searches with various customization options.

        Args:
            query (str): The search query string.
            search_depth (Literal["basic", "advanced"]): The depth of the search.
                'basic' for quick results, 'advanced' for more comprehensive results.
            topic (Literal["general", "news", "finance"]): The topic category for the search.
            time_range (Optional[Literal["day", "week", "month", "year"]]): Time range for results.
            days (int): Number of days to look back for results.
            max_results (int): Maximum number of results to return.
            include_domains (Optional[Sequence[str]]): List of domains to include in results.
            exclude_domains (Optional[Sequence[str]]): List of domains to exclude from results.
            include_answer (Union[bool, Literal["basic", "advanced"]]): Whether to include an AI-generated answer.
            include_raw_content (bool): Whether to include raw content in results.
            include_images (bool): Whether to include images in results.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: A dictionary containing the search results and metadata.

        """
        timeout = min(timeout, 120)
        response_dict = await self._search(
            query,
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

    async def _extract(
        self,
        urls: Union[List[str], str],
        include_images: bool = False,
        extract_depth: Literal["basic", "advanced"] = "basic",
        timeout: int = 60,
        **kwargs,
    ) -> dict:
        """Internal method to perform an asynchronous content extraction request.

        Args:
            urls (Union[List[str], str]): A single URL or list of URLs to extract content from.
            include_images (bool): Whether to include images in the extracted content.
            extract_depth (Literal["basic", "advanced"]): The depth of content extraction.
                'basic' for main content only, 'advanced' for more comprehensive extraction.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: The API response containing extracted content.

        Raises:
            UsageLimitExceededError: If API usage limit is exceeded.
            ForbiddenError: If the request is forbidden.
            InvalidAPIKeyError: If the API key is invalid.
            BadRequestError: If the request is malformed.
            httpx.HTTPError: For other HTTP errors.
        """
        data = {
            "urls": urls,
            "include_images": include_images,
            "extract_depth": extract_depth,
        }
        if kwargs:
            data.update(kwargs)

        timeout = min(timeout, 120)

        async with self._client_creator() as client:
            response = await client.post(
                "/extract", content=json.dumps(data), timeout=timeout
            )

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
            elif response.status_code in [403, 432, 433]:
                raise ForbiddenError(detail)
            elif response.status_code == 401:
                raise InvalidAPIKeyError(detail)
            elif response.status_code == 400:
                raise BadRequestError(detail)
            else:
                raise response.raise_for_status()

    async def extract(
        self,
        urls: Union[List[str], str],  # Accept a list of URLs or a single URL
        include_images: bool = False,
        extract_depth: Literal["basic", "advanced"] = "basic",
        timeout: int = 60,
        **kwargs,  # Accept custom arguments
    ) -> dict:
        """Extract content from one or more URLs using the Tavily API asynchronously.

        This method provides a high-level interface for performing asynchronous content
        extraction from web pages, with options for controlling the extraction depth
        and including images.

        Args:
            urls (Union[List[str], str]): A single URL or list of URLs to extract content from.
            include_images (bool): Whether to include images in the extracted content.
            extract_depth (Literal["basic", "advanced"]): The depth of content extraction.
                'basic' for main content only, 'advanced' for more comprehensive extraction.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: A dictionary containing the extracted content and metadata.

        """
        timeout = min(timeout, 120)
        response_dict = await self._extract(
            urls,
            include_images,
            extract_depth,
            timeout,
            **kwargs,
        )

        tavily_results = response_dict.get("results", [])
        failed_results = response_dict.get("failed_results", [])

        response_dict["results"] = tavily_results
        response_dict["failed_results"] = failed_results

        return response_dict

    async def _crawl(
        self,
        url: str,
        max_depth: int = None,
        max_breadth: int = None,
        limit: int = None,
        instructions: str = None,
        select_paths: Sequence[str] = None,
        select_domains: Sequence[str] = None,
        exclude_paths: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        allow_external: bool = None,
        include_images: bool = None,
        categories: Sequence[AllowedCategory] = None,
        extract_depth: Literal["basic", "advanced"] = None,
        timeout: int = 60,
        **kwargs,
    ) -> dict:
        """Internal method to perform an asynchronous website crawl request.

        Args:
            url (str): The starting URL for the crawl.
            max_depth (Optional[int]): Maximum depth of the crawl.
            max_breadth (Optional[int]): Maximum number of pages to crawl at each depth.
            limit (Optional[int]): Maximum total number of pages to crawl.
            instructions (Optional[str]): Custom instructions for the crawler.
            select_paths (Optional[Sequence[str]]): URL patterns to include in the crawl.
            select_domains (Optional[Sequence[str]]): Domains to include in the crawl.
            exclude_paths (Optional[Sequence[str]]): URL patterns to exclude from the crawl.
            exclude_domains (Optional[Sequence[str]]): Domains to exclude from the crawl.
            allow_external (Optional[bool]): Whether to allow crawling external domains.
            include_images (Optional[bool]): Whether to include images in the crawl.
            categories (Optional[Sequence[AllowedCategory]]): Content categories to include.
            extract_depth (Optional[Literal["basic", "advanced"]]): Depth of content extraction.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: The API response containing crawl results.

        Raises:
            UsageLimitExceededError: If API usage limit is exceeded.
            ForbiddenError: If the request is forbidden.
            InvalidAPIKeyError: If the API key is invalid.
            BadRequestError: If the request is malformed.
            httpx.HTTPError: For other HTTP errors.
        """
        data = {
            "url": url,
            "max_depth": max_depth,
            "max_breadth": max_breadth,
            "limit": limit,
            "instructions": instructions,
            "select_paths": select_paths,
            "select_domains": select_domains,
            "exclude_paths": exclude_paths,
            "exclude_domains": exclude_domains,
            "allow_external": allow_external,
            "categories": categories,
            "include_images": include_images,
            "extract_depth": extract_depth,
        }

        if kwargs:
            data.update(kwargs)

        data = {k: v for k, v in data.items() if v is not None}

        timeout = min(timeout, 120)

        async with self._client_creator() as client:
            response = await client.post(
                "/crawl", content=json.dumps(data), timeout=timeout
            )
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
                elif response.status_code in [403, 432, 433]:
                    raise ForbiddenError(detail)
                elif response.status_code == 401:
                    raise InvalidAPIKeyError(detail)
                elif response.status_code == 400:
                    raise BadRequestError(detail)
                else:
                    raise response.raise_for_status()

    async def crawl(
        self,
        url: str,
        max_depth: int = None,
        max_breadth: int = None,
        limit: int = None,
        instructions: str = None,
        select_paths: Sequence[str] = None,
        select_domains: Sequence[str] = None,
        exclude_paths: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        allow_external: bool = None,
        categories: Sequence[AllowedCategory] = None,
        extract_depth: Literal["basic", "advanced"] = None,
        include_images: bool = None,
        timeout: int = 60,
        **kwargs,
    ) -> dict:
        """Crawl a website using the Tavily API asynchronously.

        This method provides a high-level interface for performing asynchronous website
        crawling with various customization options for controlling the crawl behavior
        and content extraction.

        Args:
            url (str): The starting URL for the crawl.
            max_depth (Optional[int]): Maximum depth of the crawl.
            max_breadth (Optional[int]): Maximum number of pages to crawl at each depth.
            limit (Optional[int]): Maximum total number of pages to crawl.
            instructions (Optional[str]): Custom instructions for the crawler.
            select_paths (Optional[Sequence[str]]): URL patterns to include in the crawl.
            select_domains (Optional[Sequence[str]]): Domains to include in the crawl.
            exclude_paths (Optional[Sequence[str]]): URL patterns to exclude from the crawl.
            exclude_domains (Optional[Sequence[str]]): Domains to exclude from the crawl.
            allow_external (Optional[bool]): Whether to allow crawling external domains.
            include_images (Optional[bool]): Whether to include images in the crawl.
            categories (Optional[Sequence[AllowedCategory]]): Content categories to include.
            extract_depth (Optional[Literal["basic", "advanced"]]): Depth of content extraction.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            dict: A dictionary containing the crawl results and metadata.

        Example:
            >>> import asyncio
            >>> async def main():
            ...     client = AsyncTavilyClient(api_key="your-api-key")
            ...     results = await client.crawl(
            ...         url="https://example.com",
            ...         max_depth=2,
            ...         max_breadth=10,
            ...         include_images=True
            ...     )
            ...     print(results["pages"])
            >>> asyncio.run(main())
        """
        timeout = min(timeout, 120)
        response_dict = await self._crawl(
            url,
            max_depth=max_depth,
            max_breadth=max_breadth,
            limit=limit,
            instructions=instructions,
            select_paths=select_paths,
            select_domains=select_domains,
            exclude_paths=exclude_paths,
            exclude_domains=exclude_domains,
            allow_external=allow_external,
            categories=categories,
            extract_depth=extract_depth,
            include_images=include_images,
            timeout=timeout,
            **kwargs,
        )

        return response_dict

    async def _map(
        self,
        url: str,
        max_depth: int = None,
        max_breadth: int = None,
        limit: int = None,
        instructions: str = None,
        select_paths: Sequence[str] = None,
        select_domains: Sequence[str] = None,
        exclude_paths: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        allow_external: bool = None,
        include_images: bool = None,
        categories: Sequence[AllowedCategory] = None,
        timeout: int = 60,
        **kwargs,
    ) -> dict:
        """
        Internal map method to send the request to the API.
        """
        data = {
            "url": url,
            "max_depth": max_depth,
            "max_breadth": max_breadth,
            "limit": limit,
            "instructions": instructions,
            "select_paths": select_paths,
            "select_domains": select_domains,
            "exclude_paths": exclude_paths,
            "exclude_domains": exclude_domains,
            "allow_external": allow_external,
            "include_images": include_images,
            "categories": categories,
        }

        if kwargs:
            data.update(kwargs)

        data = {k: v for k, v in data.items() if v is not None}

        timeout = min(timeout, 120)

        async with self._client_creator() as client:
            response = await client.post(
                "/map", content=json.dumps(data), timeout=timeout
            )
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
                elif response.status_code in [403, 432, 433]:
                    raise ForbiddenError(detail)
                elif response.status_code == 401:
                    raise InvalidAPIKeyError(detail)
                elif response.status_code == 400:
                    raise BadRequestError(detail)
                else:
                    raise response.raise_for_status()

    async def map(
        self,
        url: str,
        max_depth: int = None,
        max_breadth: int = None,
        limit: int = None,
        instructions: str = None,
        select_paths: Sequence[str] = None,
        select_domains: Sequence[str] = None,
        exclude_paths: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        allow_external: bool = None,
        include_images: bool = None,
        categories: Sequence[AllowedCategory] = None,
        timeout: int = 60,
        **kwargs,
    ) -> dict:
        """
        Combined map method.

        """
        timeout = min(timeout, 120)
        response_dict = await self._map(
            url,
            max_depth=max_depth,
            max_breadth=max_breadth,
            limit=limit,
            instructions=instructions,
            select_paths=select_paths,
            select_domains=select_domains,
            exclude_paths=exclude_paths,
            exclude_domains=exclude_domains,
            allow_external=allow_external,
            include_images=include_images,
            categories=categories,
            timeout=timeout,
            **kwargs,
        )

        return response_dict

    async def get_search_context(
        self,
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
        """Get a contextual summary of search results for a query asynchronously. Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        This method performs an asynchronous search and returns a concise summary
        of the most relevant information found, formatted as a context string.

        Args:
            query (str): The search query string.
            search_depth (Literal["basic", "advanced"]): The depth of the search.
            topic (Literal["general", "news", "finance"]): The topic category for the search.
            days (int): Number of days to look back for results.
            max_results (int): Maximum number of results to include in the context.
            include_domains (Optional[Sequence[str]]): List of domains to include in results.
            exclude_domains (Optional[Sequence[str]]): List of domains to exclude from results.
            max_tokens (int): Maximum number of tokens in the generated context.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            str: A string containing the contextual summary of search results.

        """
        timeout = min(timeout, 120)
        response_dict = await self._search(
            query,
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
        context = [
            {"url": source["url"], "content": source["content"]} for source in sources
        ]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    async def qna_search(
        self,
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
        """Perform an asynchronous question-answering search using the Tavily API.

        This method performs an asynchronous search and returns a direct answer to
        the query, synthesized from the most relevant search results. Search depth is advanced by default to get the best answer.

        Args:
            query (str): The question to answer.
            search_depth (Literal["basic", "advanced"]): The depth of the search.
            topic (Literal["general", "news", "finance"]): The topic category for the search.
            days (int): Number of days to look back for results.
            max_results (int): Maximum number of results to consider for the answer.
            include_domains (Optional[Sequence[str]]): List of domains to include in results.
            exclude_domains (Optional[Sequence[str]]): List of domains to exclude from results.
            timeout (int): Request timeout in seconds.
            **kwargs: Additional parameters to pass to the API.

        Returns:
            str: A string containing the answer to the query.

        Example:
            >>> import asyncio
            >>> async def main():
            ...     client = AsyncTavilyClient(api_key="your-api-key")
            ...     answer = await client.qna_search(
            ...         query="What is the capital of France?",
            ...         search_depth="advanced"
            ...     )
            ...     print(answer)
            >>> asyncio.run(main())
        """
        timeout = min(timeout, 120)
        response_dict = await self._search(
            query,
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

    async def get_company_info(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "advanced",
        max_results: int = 5,
        timeout: int = 60,
    ) -> Sequence[dict]:
        """Get comprehensive information about a company asynchronously. Search depth is advanced by default to get the best answer.

        This method performs an asynchronous specialized search to gather detailed
        information about a company, including its description, financial data,
        and recent news.

        Args:
            query (str): The company name or identifier to search for.
            search_depth (Literal["basic", "advanced"]): The depth of the search.
            max_results (int): Maximum number of results to return.
            timeout (int): Request timeout in seconds.

        Returns:
            Sequence[dict]: A sequence of dictionaries containing company information.
        """
        timeout = min(timeout, 120)

        async def _perform_search(topic: str):
            return await self._search(
                query,
                search_depth=search_depth,
                topic=topic,
                max_results=max_results,
                include_answer=False,
                timeout=timeout,
            )

        all_results = []
        for data in await asyncio.gather(
            *[_perform_search(topic) for topic in self._company_info_tags]
        ):
            if "results" in data:
                all_results.extend(data["results"])

        # Sort all the results by score in descending order and take the top 'max_results' items
        sorted_results = sorted(all_results, key=lambda x: x["score"], reverse=True)[
            :max_results
        ]

        return sorted_results
