import asyncio
import json
import os
from typing import Literal, Sequence, Optional, List, Union, AsyncGenerator, Awaitable

import httpx

from .utils import get_max_items_from_list
from .errors import UsageLimitExceededError, InvalidAPIKeyError, MissingAPIKeyError, BadRequestError, ForbiddenError, TimeoutError


class AsyncTavilyClient:
    """
    Async Tavily API client class.
    """

    def __init__(self, api_key: Optional[str] = None,
                 company_info_tags: Sequence[str] = ("news", "general", "finance"),
                 proxies: Optional[dict[str, str]] = None,
                 api_base_url: Optional[str] = None,
                 client_source: Optional[str] = None):
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

        self._api_base_url = api_base_url or "https://api.tavily.com"
        self._client_creator = lambda: httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "X-Client-Source": client_source or "tavily-python"
            },
            base_url=self._api_base_url,
            mounts=proxy_mounts
        )
        self._company_info_tags = company_info_tags

    async def _search(
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
        Internal search method to send the request to the API.
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
        }

        data = {k: v for k, v in data.items() if v is not None}

        if kwargs:
            data.update(kwargs)

        timeout = min(timeout, 120)

        async with self._client_creator() as client:
            try:
                response = await client.post("/search", content=json.dumps(data), timeout=timeout)
            except httpx.TimeoutException:
                raise TimeoutError(timeout)

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

    async def search(self,
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
                     **kwargs,  # Accept custom arguments
                     ) -> dict:
        """
        Combined search method. Set search_depth to either "basic" or "advanced".
        """
        timeout = min(timeout, 120)
        response_dict = await self._search(query,
                                           search_depth=search_depth,
                                           topic=topic,
                                           time_range=time_range,
                                           start_date=start_date,
                                           end_date=end_date,
                                           days=days,
                                           max_results=max_results,
                                           include_domains=include_domains,
                                           exclude_domains=exclude_domains,
                                           include_answer=include_answer,
                                           include_raw_content=include_raw_content,
                                           include_images=include_images,
                                           timeout=timeout,
                                           country=country,
                                           auto_parameters=auto_parameters,
                                           include_favicon=include_favicon,
                                           include_usage=include_usage,
                                           **kwargs,
                                           )

        tavily_results = response_dict.get("results", [])

        response_dict["results"] = tavily_results

        return response_dict

    async def _extract(
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
            **kwargs
    ) -> dict:
        """
        Internal extract method to send the request to the API.
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
        }

        data = {k: v for k, v in data.items() if v is not None}

        if kwargs:
            data.update(kwargs)

        async with self._client_creator() as client:
            try:
                response = await client.post("/extract", content=json.dumps(data), timeout=timeout)
            except httpx.TimeoutException:
                raise TimeoutError(timeout)

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

    async def extract(self,
                      urls: Union[List[str], str],  # Accept a list of URLs or a single URL
                      include_images: bool = None,
                      extract_depth: Literal["basic", "advanced"] = None,
                      format: Literal["markdown", "text"] = None,
                      timeout: float = 30,
                      include_favicon: bool = None,
                      include_usage: bool = None,
                      query: str = None,
                      chunks_per_source: int = None,
                      **kwargs,  # Accept custom arguments
                      ) -> dict:
        """
        Combined extract method.
        include_favicon: If True, include the favicon in the extraction results.
        """
        response_dict = await self._extract(urls,
                                            include_images,
                                            extract_depth,
                                            format,
                                            timeout,
                                            include_favicon=include_favicon,
                                            include_usage=include_usage,
                                            query=query,
                                            chunks_per_source=chunks_per_source,
                                            **kwargs,
                                            )

        tavily_results = response_dict.get("results", [])
        failed_results = response_dict.get("failed_results", [])

        response_dict["results"] = tavily_results
        response_dict["failed_results"] = failed_results

        return response_dict
    
    async def _crawl(self,
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
               **kwargs
               ) -> dict:
        """
        Internal crawl method to send the request to the API.
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
            "extract_depth": extract_depth,
            "format": format,
            "timeout": timeout,
            "include_favicon": include_favicon,
            "include_usage": include_usage,
            "chunks_per_source": chunks_per_source,
        }

        if kwargs:
            data.update(kwargs)

        data = {k: v for k, v in data.items() if v is not None}

        async with self._client_creator() as client:
            try:
                response = await client.post("/crawl", content=json.dumps(data), timeout=timeout)
            except httpx.TimeoutException:
                raise TimeoutError(timeout)

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

    async def crawl(self,
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
                    extract_depth: Literal["basic", "advanced"] = None,
                    include_images: bool = None,
                    format: Literal["markdown", "text"] = None,
                    timeout: float = 150,
                    include_favicon: bool = None,
                    include_usage: bool = None,
                    chunks_per_source: int = None,
                    **kwargs
                    ) -> dict:
        """
        Combined crawl method.
        
        """
        response_dict = await self._crawl(url,
                                    max_depth=max_depth,
                                    max_breadth=max_breadth,
                                    limit=limit,
                                    instructions=instructions,
                                    select_paths=select_paths,
                                    select_domains=select_domains,
                                    exclude_paths=exclude_paths,
                                    exclude_domains=exclude_domains,
                                    allow_external=allow_external,
                                    extract_depth=extract_depth,
                                    include_images=include_images,
                                    format=format,
                                    timeout=timeout,
                                    include_favicon=include_favicon,
                                    include_usage=include_usage,
                                    chunks_per_source=chunks_per_source,
                                    **kwargs)

        return response_dict
    
    async def _map(self,
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
               **kwargs
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
            "timeout": timeout,
            "include_usage": include_usage,
        }

        if kwargs:
            data.update(kwargs)

        data = {k: v for k, v in data.items() if v is not None}

        async with self._client_creator() as client:
            try:
                response = await client.post("/map", content=json.dumps(data), timeout=timeout)
            except httpx.TimeoutException:
                raise TimeoutError(timeout)

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

    async def map(self,
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
                    **kwargs
                    ) -> dict:
        """
        Combined map method.

        """
        response_dict = await self._map(url,
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
                                    timeout=timeout,
                                    include_usage=include_usage,
                                    **kwargs)

        return response_dict

    async def get_search_context(self,
                                 query: str,
                                 search_depth: Literal["basic", "advanced"] = "basic",
                                 topic: Literal["general", "news", "finance"] = "general",
                                 days: int = 7,
                                 max_results: int = 5,
                                 include_domains: Sequence[str] = None,
                                 exclude_domains: Sequence[str] = None,
                                 max_tokens: int = 4000,
                                 timeout: float = 60,
                                 country: str = None,
                                 include_favicon: bool = None,
                                 **kwargs,  # Accept custom arguments
                                 ) -> str:
        """
        Get the search context for a query. Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        max_tokens: The maximum number of tokens to return (based on openai token compute). Defaults to 4000.

        Returns a string of JSON containing the search context up to context limit.
        """
        timeout = min(timeout, 120)
        response_dict = await self._search(query,
                                           search_depth=search_depth,
                                           topic=topic,
                                           days=days,
                                           max_results=max_results,
                                           include_domains=include_domains,
                                           exclude_domains=exclude_domains,
                                           include_answer=False,
                                           include_raw_content=False,
                                           include_images=False,
                                           timeout = timeout,
                                           country=country,
                                           include_favicon=include_favicon,
                                           **kwargs,
                                           )
        sources = response_dict.get("results", [])
        context = [{"url": source["url"], "content": source["content"]} for source in sources]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    async def qna_search(self,
                         query: str,
                         search_depth: Literal["basic", "advanced"] = "advanced",
                         topic: Literal["general", "news", "finance"] = "general",
                         days: int = 7,
                         max_results: int = 5,
                         include_domains: Sequence[str] = None,
                         exclude_domains: Sequence[str] = None,
                         timeout: float = 60,
                         country: str = None,
                         include_favicon: bool = None,
                         **kwargs,  # Accept custom arguments
                         ) -> str:
        """
        Q&A search method. Search depth is advanced by default to get the best answer.
        """
        timeout = min(timeout, 120)
        response_dict = await self._search(query,
                                           search_depth=search_depth,
                                           topic=topic,
                                           days=days,
                                           max_results=max_results,
                                           include_domains=include_domains,
                                           exclude_domains=exclude_domains,
                                           include_raw_content=False,
                                           include_images=False,
                                           include_answer=True,
                                           timeout = timeout,
                                           country=country,
                                           include_favicon=include_favicon,
                                           **kwargs,
                                           )
        return response_dict.get("answer", "")

    async def get_company_info(self,
                               query: str,
                               search_depth: Literal["basic", "advanced"] = "advanced",
                               max_results: int = 5,
                               timeout: float = 60,
                               country: str = None,
                               ) -> Sequence[dict]:
        """ Company information search method. Search depth is advanced by default to get the best answer. """
        timeout = min(timeout, 120)

        async def _perform_search(topic: str):
            return await self._search(query,
                                      search_depth=search_depth,
                                      topic=topic,
                                      max_results=max_results,
                                      include_answer=False,
                                      timeout = timeout,
                                      country=country)

        all_results = []
        for data in await asyncio.gather(*[_perform_search(topic) for topic in self._company_info_tags]):
            if "results" in data:
                all_results.extend(data["results"])

        # Sort all the results by score in descending order and take the top 'max_results' items
        sorted_results = sorted(all_results, key=lambda x: x["score"], reverse=True)[:max_results]

        return sorted_results

    def _research(self,
                  input: str,
                  model: Literal["mini", "pro", "auto"] = None,
                  output_schema: dict = None,
                  stream: bool = False,
                  citation_format: Literal["numbered", "mla", "apa", "chicago"] = "numbered",
                  timeout: Optional[float] = None,
                  **kwargs
                  ) -> Union[AsyncGenerator[bytes, None], Awaitable[dict]]:
        """
        Internal research method to send the request to the API.
        """
        data = {
            "input": input,
            "model": model,
            "output_schema": output_schema,
            "stream": stream,
            "citation_format": citation_format,
        }

        data = {k: v for k, v in data.items() if v is not None}

        if kwargs:
            data.update(kwargs)

        if stream:
            async def stream_generator() -> AsyncGenerator[bytes, None]:
                try:
                    async with self._client_creator() as client:
                        async with client.stream(
                            "POST",
                            "/research",
                            content=json.dumps(data),
                            timeout=timeout
                        ) as response:
                            if response.status_code != 200:
                                try:
                                    error_text = await response.aread()
                                    error_text = error_text.decode('utf-8') if isinstance(error_text, bytes) else error_text
                                except Exception:
                                    error_text = "Unknown error"
                                
                                if response.status_code == 429:
                                    raise UsageLimitExceededError(error_text)
                                elif response.status_code in [403,432,433]:
                                    raise ForbiddenError(error_text)
                                elif response.status_code == 401:
                                    raise InvalidAPIKeyError(error_text)
                                elif response.status_code == 400:
                                    raise BadRequestError(error_text)
                                else:
                                    raise Exception(f"Error {response.status_code}: {error_text}")
                            
                            async for chunk in response.aiter_bytes():
                                if chunk:
                                    yield chunk
                except httpx.TimeoutException:
                    raise TimeoutError(timeout)
                except Exception as e:
                    raise Exception(f"Error during research stream: {str(e)}")
            
            return stream_generator()
        else:
            async def _make_request():
                async with self._client_creator() as client:
                    try:
                        response = await client.post("/research", content=json.dumps(data), timeout=timeout)
                    except httpx.TimeoutException:
                        raise TimeoutError(timeout)

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
            
            return _make_request()

    async def research(self,
                       input: str,
                       model: Literal["mini", "pro", "auto"] = None,
                       output_schema: dict = None,
                       stream: bool = False,
                       citation_format: Literal["numbered", "mla", "apa", "chicago"] = "numbered",
                       timeout: Optional[float] = None,
                       **kwargs
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
        result = self._research(
                input=input,
                model=model,
                output_schema=output_schema,
                stream=stream,
                citation_format=citation_format,
                timeout=timeout,
                **kwargs
        )
        if stream:
            return result # Don't await the result, it's an AsyncGenerator that will be lazy and only execute when iterated over with async for
        else:
            return await result 

    async def get_research(self,
                           request_id: str
                           ) -> dict:
        """
        Get research results by request_id.
        
        Args:
            request_id: The research request ID.
        
        Returns:
            dict: Research response containing request_id, created_at, completed_at, status, content, and sources.
        """
        async with self._client_creator() as client:
            try:
                response = await client.get(f"/research/{request_id}")
            except Exception as e:
                raise Exception(f"Error getting research: {e}")

            if response.status_code in (200, 202):
                data = response.json()
                return data
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
