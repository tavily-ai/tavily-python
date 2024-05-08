import asyncio
import json
from typing import Literal, Sequence

import httpx

from tavily.utils import get_max_items_from_list


class AsyncTavilyClient:
    def __init__(self, api_key: str, company_info_tags: Sequence[str] = ("news", "general", "finance")):
        self._base_data = {
            "api_key": api_key,
        }
        self._client_creator = lambda: httpx.AsyncClient(
            headers={
                "Content-Type": "application/json",
            },
            base_url="https://api.tavily.com",
            timeout=180,
        )
        self._company_info_tags = company_info_tags

    async def _search(
        self,
        query: str,
        search_depth: Literal["basic", "advanced"] = "basic",
        topic: str = "general",
        days: int = 2,
        max_results: int = 5,
        include_domains: Sequence[str] = None,
        exclude_domains: Sequence[str] = None,
        include_answer: bool = False,
        include_raw_content: bool = False,
        include_images: bool = False,
        use_cache: bool = True,
    ) -> dict:
        """
        Internal search method to send the request to the API.
        """
        data = {
            **self._base_data,
            "query": query,
            "search_depth": search_depth,
            "topic": topic,
            "days": days,
            "include_answer": include_answer,
            "include_raw_content": include_raw_content,
            "max_results": max_results,
            "include_domains": include_domains or None,
            "exclude_domains": exclude_domains or None,
            "include_images": include_images,
            "use_cache": use_cache,
        }
        async with self._client_creator() as client:
            response = await client.post("/search", data=json.dumps(data))

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()  # Raises a HTTPError if the HTTP request returned an unsuccessful status code

    async def search(self, query: str, search_depth: Literal["basic", "advanced"] = "basic", **kwargs) -> dict:
        """
        Combined search method. Set search_depth to either "basic" or "advanced".
        """
        return await self._search(query, search_depth=search_depth, **kwargs)

    async def get_search_context(
        self, query: str, search_depth: Literal["basic", "advanced"] = "basic", max_tokens=4000, **kwargs
    ):
        """
        Get the search context for a query. Useful for getting only related content from retrieved websites
        without having to deal with context extraction and limitation yourself.

        max_tokens: The maximum number of tokens to return (based on openai token compute). Defaults to 4000.

        Returns a string of JSON containing the search context up to context limit.
        """
        search_result = await self._search(query, search_depth, **kwargs)
        sources = search_result.get("results", [])
        context = [{"url": obj["url"], "content": obj["content"]} for obj in sources]
        return json.dumps(get_max_items_from_list(context, max_tokens))

    async def qna_search(self, query: str, search_depth: Literal["basic", "advanced"] = "advanced", **kwargs) -> str:
        """
        Q&A search method. Search depth is advanced by default to get the best answer.
        """
        search_result = await self._search(query, search_depth=search_depth, include_answer=True, **kwargs)
        return search_result.get("answer", "")

    async def get_company_info(
        self, query: str, search_depth: Literal["basic", "advanced"] = "basic", max_results=5, **kwargs
    ) -> list[dict]:
        """Q&A search method. Search depth is advanced by default to get the best answer."""

        async def _perform_search(topic: str):
            return await self._search(
                query, search_depth=search_depth, topic=topic, max_results=max_results, include_answer=False, **kwargs
            )

        all_results = []
        for data in await asyncio.gather(*[_perform_search(topic) for topic in self._company_info_tags]):
            if "results" in data:
                all_results.extend(data["results"])

        # Sort all the results by score in descending order and take the top 'max_results' items
        sorted_results = sorted(all_results, key=lambda x: x["score"], reverse=True)[:max_results]

        return sorted_results
