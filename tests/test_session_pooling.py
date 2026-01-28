"""
Tests for session pooling functionality in both sync and async clients.
"""
import asyncio
import pytest

import tavily.tavily as sync_tavily
import tavily.async_tavily as async_tavily
from tests.request_intercept import intercept_requests, clear_interceptor


dummy_response = {
    "query": "test",
    "results": [{"title": "Test", "url": "https://test.com", "content": "Test content", "score": 0.99}],
    "response_time": 0.1
}


# =============================================================================
# SYNC CLIENT TESTS
# =============================================================================

class TestSyncSessionPooling:
    """Test sync client session pooling and lifecycle."""

    @pytest.fixture
    def interceptor(self):
        yield intercept_requests(sync_tavily)
        clear_interceptor(sync_tavily)

    def test_context_manager(self, interceptor):
        """Test that sync client works with context manager."""
        interceptor.set_response(200, json=dummy_response)

        with sync_tavily.TavilyClient(api_key="tvly-test") as client:
            response = client.search("test query")
            assert response["results"][0]["title"] == "Test"

    def test_close_method(self, interceptor):
        """Test that close() method works without error."""
        interceptor.set_response(200, json=dummy_response)

        client = sync_tavily.TavilyClient(api_key="tvly-test")
        response = client.search("test query")
        assert response["results"][0]["title"] == "Test"

        # close() should not raise
        client.close()

    def test_multiple_sequential_requests(self, interceptor):
        """Test that multiple requests work with same client (connection reuse)."""
        interceptor.set_response(200, json=dummy_response)

        client = sync_tavily.TavilyClient(api_key="tvly-test")

        # Make multiple requests with same client
        for i in range(3):
            response = client.search(f"test query {i}")
            assert response["results"][0]["title"] == "Test"

        client.close()

    def test_context_manager_multiple_requests(self, interceptor):
        """Test multiple requests within context manager."""
        interceptor.set_response(200, json=dummy_response)

        with sync_tavily.TavilyClient(api_key="tvly-test") as client:
            for i in range(3):
                response = client.search(f"test query {i}")
                assert response["results"][0]["title"] == "Test"


# =============================================================================
# ASYNC CLIENT TESTS
# =============================================================================

class TestAsyncSessionPooling:
    """Test async client session pooling and lifecycle."""

    @pytest.fixture
    def interceptor(self):
        yield intercept_requests(async_tavily)
        clear_interceptor(async_tavily)

    def test_context_manager(self, interceptor):
        """Test that async client works with async context manager."""
        interceptor.set_response(200, json=dummy_response)

        async def run():
            async with async_tavily.AsyncTavilyClient(api_key="tvly-test") as client:
                response = await client.search("test query")
                assert response["results"][0]["title"] == "Test"

        asyncio.run(run())

    def test_close_method(self, interceptor):
        """Test that close() method works without error."""
        interceptor.set_response(200, json=dummy_response)

        async def run():
            client = async_tavily.AsyncTavilyClient(api_key="tvly-test")
            response = await client.search("test query")
            assert response["results"][0]["title"] == "Test"

            # close() should not raise
            await client.close()

        asyncio.run(run())

    def test_multiple_sequential_requests(self, interceptor):
        """Test that multiple requests work with same client (connection reuse)."""
        interceptor.set_response(200, json=dummy_response)

        async def run():
            client = async_tavily.AsyncTavilyClient(api_key="tvly-test")

            # Make multiple requests with same client
            for i in range(3):
                response = await client.search(f"test query {i}")
                assert response["results"][0]["title"] == "Test"

            await client.close()

        asyncio.run(run())

    def test_context_manager_multiple_requests(self, interceptor):
        """Test multiple requests within async context manager."""
        interceptor.set_response(200, json=dummy_response)

        async def run():
            async with async_tavily.AsyncTavilyClient(api_key="tvly-test") as client:
                for i in range(3):
                    response = await client.search(f"test query {i}")
                    assert response["results"][0]["title"] == "Test"

        asyncio.run(run())

    def test_concurrent_requests_same_client(self, interceptor):
        """Test concurrent requests using same client."""
        interceptor.set_response(200, json=dummy_response)

        async def run():
            async with async_tavily.AsyncTavilyClient(api_key="tvly-test") as client:
                # Run multiple searches concurrently
                tasks = [client.search(f"query {i}") for i in range(3)]
                results = await asyncio.gather(*tasks)

                assert len(results) == 3
                for result in results:
                    assert result["results"][0]["title"] == "Test"

        asyncio.run(run())
