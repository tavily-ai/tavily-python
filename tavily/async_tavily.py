import asyncio
import json
import os
from typing import Literal, Sequence, Optional, List, Union, AsyncGenerator

import httpx

from .utils import get_max_items_from_list
from .errors import UsageLimitExceededError, InvalidAPIKeyError, MissingAPIKeyError, BadRequestError, ForbiddenError, TimeoutError


class AsyncTavilyClient:
    """
    Async Tavily API client class.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        company_info_tags: Sequence[str] = ("news", "general", "finance"),
        proxies: Optional[dict[str, str]] = None,
        api_base_url: Optional[str] = None,
        client_source: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
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
            {scheme: httpx.AsyncHTTPTransport(proxy=proxy) for scheme, proxy in mapped_proxies.items()}
            if mapped_proxies
            else None
        )

        tavily_project = project_id or os.getenv("TAVILY_PROJECT")

        self._client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-Client-Source": client_source or "tavily-python",
                **({"X-Project-ID": tavily_project} if tavily_project else {})
            },
            base_url=api_base_url or "https://api.tavily.com",
            mounts=proxy_mounts,
        )
        self._company_info_tags = company_info_tags

    async def close(self) -> None:
        """Close the client and release connection pool resources."""
        await self._client.aclose()

    async def __aenter__(self) -> "AsyncTavilyClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle non-200 HTTP responses by raising appropriate exceptions."""
        detail = ""
        try:
            detail = response.json().get("detail", {}).get("error", None)
        except Exception:
            pass

        status = response.status_code
        if status == 429:
            raise UsageLimitExceededError(detail)
        if status in (403, 432, 433):
            raise ForbiddenError(detail)
        if status == 401:
            raise InvalidAPIKeyError(detail)
        if status == 400:
            raise BadRequestError(detail)
        response.raise_for_status()

    async def _post(self, endpoint: str, data: dict, timeout: float) -> dict:
        """Make a POST request and handle response/errors."""
        try:
            response = await self._client.post(endpoint, content=json.dumps(data), timeout=timeout)
        except httpx.TimeoutException:
            raise TimeoutError(timeout)

        if response.status_code == 200:
            return response.json()
        self._handle_error_response(response)

    async def search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = None,
        topic: Literal["general", "news", "finance"] = None,
        time_range: Literal["day", "week", "month", "year"] = None,
        start_date: str = None,
        end_date: str = None,
        days: int = None,
        max_results: int = None,
        include_domains: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        include_answer: Union[bool, Literal["basic", "advanced"]] = None,
        include_raw_content: Union[bool, Literal["markdown", "text"]] = None,
        include_images: bool = None,
        timeout: float = 60,
        country: str = None,
        auto_parameters: bool = None,
        include_favicon: bool = None,
        include_usage: bool = None,
        **kwargs,
    ) -> dict:
        """
        Search method. Set search_depth to either "basic", "advanced", "fast", or "ultra-fast".
        """
        data = {
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "time_range": time_range,
            "start_date": start_date,
            "end_date": end_date,
            "days": days,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "include_images": include_images,
            "country": country,
            "auto_parameters": auto_parameters,
            "include_favicon": include_favicon,
            "include_usage": include_usage,
            **kwargs,
        }
        data = {k: v for k, v in data.items() if v is not None}

        response_dict = await self._post("/search", data, min(timeout, 120))
        response_dict.setdefault("results", [])
        return response_dict

    async def extract(
        self,
        urls: Union[List[str], str],
        include_images: bool = None,
        extract_depth: Literal["basic", "advanced"] = None,
        format: Literal["markdown", "text"] = None,
        timeout: float = 30,
        include_favicon: bool = None,
        include_usage: bool = None,
        query: str = None,
        chunks_per_source: int = None,
        **kwargs,
    ) -> dict:
        """
        Extract method to extract content from URLs.

        Args:
            urls: A single URL or list of URLs to extract content from.
            include_favicon: If True, include the favicon in the extraction results.
        """
        data = {
            "urls": urls,
            "include_images": include_images,
            "extract_depth": extract_depth,
            "format": format,
            "timeout": timeout,
            "include_favicon": include_favicon,
            "include_usage": include_usage,
            "query": query,
            "chunks_per_source": chunks_per_source,
            **kwargs,
        }
        data = {k: v for k, v in data.items() if v is not None}

        response_dict = await self._post("/extract", data, timeout)
        response_dict.setdefault("results", [])
        response_dict.setdefault("failed_results", [])
        return response_dict
    
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
        include_images: bool = None,
        extract_depth: Literal["basic", "advanced"] = None,
        format: Literal["markdown", "text"] = None,
        timeout: float = 150,
        include_favicon: bool = None,
        include_usage: bool = None,
        chunks_per_source: int = None,
        **kwargs,
    ) -> dict:
        """Crawl method to crawl a website and extract content."""
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
            "extract_depth": extract_depth,
            "format": format,
            "timeout": timeout,
            "include_favicon": include_favicon,
            "include_usage": include_usage,
            "chunks_per_source": chunks_per_source,
            **kwargs,
        }
        data = {k: v for k, v in data.items() if v is not None}

        return await self._post("/crawl", data, timeout)
    
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
        timeout: float = 150,
        include_usage: bool = None,
        **kwargs,
    ) -> dict:
        """Map method to discover URLs on a website."""
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
            "timeout": timeout,
            "include_usage": include_usage,
            **kwargs,
        }
        data = {k: v for k, v in data.items() if v is not None}

        return await self._post("/map", data, timeout)

    async def get_search_context(
        self,
        query: str,
        search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = "basic",
        topic: Literal["general", "news", "finance"] = "general",
        days: int = 7,
        max_results: int = 5,
        include_domains: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        max_tokens: int = 4000,
        timeout: float = 60,
        country: str = None,
        include_favicon: bool = None,
        **kwargs,
    ) -> str:
        """
        Get the search context for a query. Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        Args:
            max_tokens: The maximum number of tokens to return (based on openai token compute). Defaults to 4000.

        Returns:
            A string of JSON containing the search context up to context limit.
        """
        response_dict = await self.search(
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
            country=country,
            include_favicon=include_favicon,
            **kwargs,
        )
        sources = response_dict.get("results", [])
        context = [{"url": source["url"], "content": source["content"]} for source in sources]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    async def qna_search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = "advanced",
        topic: Literal["general", "news", "finance"] = "general",
        days: int = 7,
        max_results: int = 5,
        include_domains: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        timeout: float = 60,
        country: str = None,
        include_favicon: bool = None,
        **kwargs,
    ) -> str:
        """Q&A search method. Search depth is advanced by default to get the best answer."""
        response_dict = await self.search(
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
            country=country,
            include_favicon=include_favicon,
            **kwargs,
        )
        return response_dict.get("answer", "")

    async def get_company_info(
        self,
        query: str,
        search_depth: Literal["basic", "advanced", "fast", "ultra-fast"] = "advanced",
        max_results: int = 5,
        timeout: float = 60,
        country: str = None,
    ) -> Sequence[dict]:
        """Company information search method. Search depth is advanced by default to get the best answer."""
        async def perform_search(topic: str) -> dict:
            return await self.search(
                query,
                search_depth=search_depth,
                topic=topic,
                max_results=max_results,
                include_answer=False,
                timeout=timeout,
                country=country,
            )

        results = await asyncio.gather(*[perform_search(topic) for topic in self._company_info_tags])

        all_results = []
        for data in results:
            all_results.extend(data.get("results", []))

        return sorted(all_results, key=lambda x: x["score"], reverse=True)[:max_results]

    def _handle_stream_error(self, status_code: int, error_text: str) -> None:
        """Handle error responses during streaming."""
        if status_code == 429:
            raise UsageLimitExceededError(error_text)
        if status_code in (403, 432, 433):
            raise ForbiddenError(error_text)
        if status_code == 401:
            raise InvalidAPIKeyError(error_text)
        if status_code == 400:
            raise BadRequestError(error_text)
        raise Exception(f"Error {status_code}: {error_text}")

    async def _research_stream(
        self,
        data: dict,
        timeout: Optional[float],
    ) -> AsyncGenerator[bytes, None]:
        """Stream research results from the API."""
        try:
            async with self._client.stream(
                "POST",
                "/research",
                content=json.dumps(data),
                timeout=timeout,
            ) as response:
                if response.status_code != 200:
                    try:
                        error_bytes = await response.aread()
                        error_text = error_bytes.decode("utf-8") if isinstance(error_bytes, bytes) else error_bytes
                    except Exception:
                        error_text = "Unknown error"
                    self._handle_stream_error(response.status_code, error_text)

                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk
        except httpx.TimeoutException:
            raise TimeoutError(timeout)

    async def research(
        self,
        input: str,
        model: Literal["mini", "pro", "auto"] = None,
        output_schema: dict = None,
        stream: bool = False,
        citation_format: Literal["numbered", "mla", "apa", "chicago"] = "numbered",
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Union[dict, AsyncGenerator[bytes, None]]:
        """
        Research method to create a research task.

        Args:
            input: The research task description (required).
            model: Research depth - must be either 'mini', 'pro', or 'auto'.
            output_schema: Schema for the 'structured_output' response format (JSON Schema dict).
            stream: Whether to stream the research task.
            citation_format: Citation format - must be either 'numbered', 'mla', 'apa', or 'chicago'.
            timeout: Optional HTTP request timeout in seconds.
            **kwargs: Additional custom arguments.

        Returns:
            When stream=False: dict - the response dictionary.
            When stream=True: AsyncGenerator[bytes, None] - iterate over this to get streaming chunks.
        """
        data = {
            "input": input,
            "model": model,
            "output_schema": output_schema,
            "stream": stream,
            "citation_format": citation_format,
            **kwargs,
        }
        data = {k: v for k, v in data.items() if v is not None}

        if stream:
            return self._research_stream(data, timeout)

        return await self._post("/research", data, timeout)

    async def get_research(self, request_id: str) -> dict:
        """
        Get research results by request_id.

        Args:
            request_id: The research request ID.

        Returns:
            dict: Research response containing request_id, created_at, completed_at, status, content, and sources.
        """
        response = await self._client.get(f"/research/{request_id}")

        if response.status_code in (200, 202):
            return response.json()

        self._handle_error_response(response)
